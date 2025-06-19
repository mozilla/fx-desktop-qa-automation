import logging
import os
from collections import defaultdict

from dotenv import load_dotenv

from modules.testrail_integration import testrail_init


# Configure loggers
def setup_loggers():
    """Set up separate loggers for operational info and report output"""

    # Operational logger - for progress, debug, errors
    op_logger = logging.getLogger("operations")
    op_handler = logging.StreamHandler()
    op_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    op_logger.addHandler(op_handler)
    op_logger.setLevel(logging.INFO)

    # Report logger - for formatted output
    report_logger = logging.getLogger("report")
    report_handler = logging.StreamHandler()
    report_handler.setFormatter(logging.Formatter("%(message)s"))
    report_logger.addHandler(report_handler)
    report_logger.setLevel(logging.INFO)

    return op_logger, report_logger


# Initialize loggers
op_log, report = setup_loggers()

# Load env file from project root
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
env_file_path = os.path.join(project_root, "testrail_credentials.env")
load_dotenv(dotenv_path=env_file_path)

# TestRail project ID (Fx Desktop)
PROJECT_ID = 17

# Automation status values
AUTOMATION_STATUS = {
    1: "Untriaged",
    2: "Suitable",
    3: "Not Suitable",
    4: "Completed",
    5: "Disabled",
    None: "Not Set",
}

# Automation coverage values
AUTOMATION_COVERAGE = {1: "None", 2: "Partial", 3: "Full", None: "Not Set"}

# Sub Test Suite values
SUB_TEST_SUITE_MAPPING = {1: "Functional", 2: "Smoke", None: "Not Set"}


def get_all_suites(tr, project_id):
    """Get all suites from the project"""
    suites = tr.client.send_get(f"get_suites/{project_id}")
    op_log.info(f"Found {len(suites)} suites in project {project_id}")
    return suites


def get_all_test_cases(tr, project_id, suite_id):
    """Fetch all test cases from a suite by handling pagination."""
    all_cases = []
    offset = 0
    limit = 240  # Default limit for TestRail API is 250

    while True:
        # Build endpoint with pagination parameters
        endpoint = (
            f"get_cases/{project_id}&suite_id={suite_id}&limit={limit}&offset={offset}"
        )

        response = tr.client.send_get(endpoint)
        cases = response.get("cases", [])
        if not cases:
            break
        all_cases.extend(cases)
        # If the number of cases returned is less than the limit, we've reached the last page.
        if len(cases) < limit:
            break
        offset += limit

    return all_cases


def analyze_test_cases(cases):
    """Analyze test cases and return detailed statistics"""
    stats = {
        "total_cases": len(cases),
        "by_sub_test_suite": defaultdict(int),
        "by_automation_status": defaultdict(int),
        "by_automation_coverage": defaultdict(int),
        "by_status_coverage_combo": defaultdict(int),
        "detailed_breakdown": [],
    }

    for case in cases:
        case_id = case.get("id")
        title = case.get("title", "No Title")

        # Get Sub Test Suite(s) - use the exact field name
        sub_test_suite_raw = case.get("custom_sub_test_suites")

        automation_status = case.get("custom_automation_status")
        automation_coverage = case.get("custom_automation_coverage")

        # Get Sub Test Suite(s) - simple mapping from list to name
        sub_test_suite_raw = case.get("custom_sub_test_suites", [])
        if sub_test_suite_raw:
            sub_test_suite_id = sub_test_suite_raw[0]
            sub_test_suite_name = SUB_TEST_SUITE_MAPPING.get(
                sub_test_suite_id, "Not Set"
            )
        else:
            sub_test_suite_name = "Not Set"

        status_name = AUTOMATION_STATUS.get(
            automation_status, f"Unknown Status ({automation_status})"
        )
        coverage_name = AUTOMATION_COVERAGE.get(
            automation_coverage, f"Unknown Coverage ({automation_coverage})"
        )

        # Count by sub test suite
        stats["by_sub_test_suite"][sub_test_suite_name] += 1

        # Count by automation status
        stats["by_automation_status"][status_name] += 1

        # Count by automation coverage
        stats["by_automation_coverage"][coverage_name] += 1

        # Count by status + coverage combination
        combo = f"{status_name} + {coverage_name}"
        stats["by_status_coverage_combo"][combo] += 1

        # Store detailed breakdown
        stats["detailed_breakdown"].append(
            {
                "id": case_id,
                "title": title,
                "sub_test_suite": sub_test_suite_name,
                "automation_status": status_name,
                "automation_coverage": coverage_name,
            }
        )

    return stats


def print_suite_statistics(suite_name, suite_id, stats, show_detailed_cases=True):
    """Print detailed statistics for a suite"""
    report.info(f"\n{'=' * 80}")
    report.info(f"SUITE: {suite_name} (ID: {suite_id})")
    report.info(f"{'=' * 80}")
    report.info(f"Total Test Cases: {stats['total_cases']}")

    if stats["total_cases"] == 0:
        report.info("No test cases found in this suite.")
        return

    # Sub Test Suites Breakdown
    report.info(f"\n{'-' * 50}")
    report.info("SUB TEST SUITES BREAKDOWN:")
    report.info(f"{'-' * 50}")
    for sub_suite, count in sorted(stats["by_sub_test_suite"].items()):
        percentage = (count / stats["total_cases"]) * 100
        report.info(f"{sub_suite:30} | {count:5} cases ({percentage:5.1f}%)")

    # Automation Status Breakdown
    report.info(f"\n{'-' * 50}")
    report.info("AUTOMATION STATUS BREAKDOWN:")
    report.info(f"{'-' * 50}")
    for status, count in sorted(stats["by_automation_status"].items()):
        percentage = (count / stats["total_cases"]) * 100
        report.info(f"{status:20} | {count:5} cases ({percentage:5.1f}%)")

    # Automation Coverage Breakdown
    report.info(f"\n{'-' * 50}")
    report.info("AUTOMATION COVERAGE BREAKDOWN:")
    report.info(f"{'-' * 50}")
    for coverage, count in sorted(stats["by_automation_coverage"].items()):
        percentage = (count / stats["total_cases"]) * 100
        report.info(f"{coverage:20} | {count:5} cases ({percentage:5.1f}%)")

    # Status + Coverage Combinations
    report.info(f"\n{'-' * 70}")
    report.info("AUTOMATION STATUS + COVERAGE COMBINATIONS:")
    report.info(f"{'-' * 70}")
    for combo, count in sorted(stats["by_status_coverage_combo"].items()):
        percentage = (count / stats["total_cases"]) * 100
        report.info(f"{combo:40} | {count:5} cases ({percentage:5.1f}%)")

    # Detailed test case listing with IDs and Titles
    if show_detailed_cases and stats["detailed_breakdown"]:
        report.info(f"\n{'-' * 120}")
        report.info("DETAILED TEST CASE BREAKDOWN (ID + TITLE):")
        report.info(f"{'-' * 120}")
        report.info(
            f"{'ID':8} | {'Sub Test Suite':25} | {'Status':15} | {'Coverage':10} | {'Title'}"
        )
        report.info(f"{'-' * 120}")

        # Sort by automation status, then by coverage, then by ID
        sorted_cases = sorted(
            stats["detailed_breakdown"],
            key=lambda x: (x["automation_status"], x["automation_coverage"], x["id"]),
        )

        for case in sorted_cases:
            title_truncated = (
                case["title"][:60] + "..." if len(case["title"]) > 60 else case["title"]
            )
            sub_suite_truncated = (
                case["sub_test_suite"][:23] + ".."
                if len(case["sub_test_suite"]) > 23
                else case["sub_test_suite"]
            )
            report.info(
                f"C{case['id']:7} | {sub_suite_truncated:25} | {case['automation_status']:15} | {case['automation_coverage']:10} | {title_truncated}"
            )

        report.info(f"{'-' * 120}")
        report.info(f"Total cases in this suite: {len(stats['detailed_breakdown'])}")


def print_project_summary(project_stats):
    """Print overall project summary"""
    report.info(f"\n{'=' * 80}")
    report.info("PROJECT SUMMARY")
    report.info(f"{'=' * 80}")
    report.info(f"Total Suites: {project_stats['total_suites']}")
    report.info(f"Total Test Cases: {project_stats['total_cases']}")

    if project_stats["total_cases"] == 0:
        report.info("No test cases found in project.")
        return

    # Overall Sub Test Suites
    report.info(f"\n{'-' * 60}")
    report.info("OVERALL SUB TEST SUITES:")
    report.info(f"{'-' * 60}")
    for sub_suite, count in sorted(
        project_stats["by_sub_test_suite"].items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / project_stats["total_cases"]) * 100
        report.info(f"{sub_suite:35} | {count:5} cases ({percentage:5.1f}%)")

    # Overall Automation Status
    report.info(f"\n{'-' * 50}")
    report.info("OVERALL AUTOMATION STATUS:")
    report.info(f"{'-' * 50}")
    for status, count in sorted(
        project_stats["by_automation_status"].items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / project_stats["total_cases"]) * 100
        report.info(f"{status:20} | {count:5} cases ({percentage:5.1f}%)")

    # Overall Automation Coverage
    report.info(f"\n{'-' * 50}")
    report.info("OVERALL AUTOMATION COVERAGE:")
    report.info(f"{'-' * 50}")
    for coverage, count in sorted(
        project_stats["by_automation_coverage"].items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        percentage = (count / project_stats["total_cases"]) * 100
        report.info(f"{coverage:20} | {count:5} cases ({percentage:5.1f}%)")


def print_numerical_summary(project_stats):
    """Print a focused numerical summary with totals"""
    report.info(f"\n{'=' * 80}")
    report.info("NUMERICAL SUMMARY - TOTAL COUNTS")
    report.info(f"{'=' * 80}")

    report.info("\n OVERALL TOTALS:")
    report.info(f"   Total Suites: {project_stats['total_suites']}")
    report.info(f"   Total Test Cases: {project_stats['total_cases']}")

    if project_stats["total_cases"] == 0:
        return

    report.info("\n SUB TEST SUITE TOTALS:")
    total_by_sub_suite = sorted(
        project_stats["by_sub_test_suite"].items(), key=lambda x: x[1], reverse=True
    )
    for sub_suite, count in total_by_sub_suite:
        percentage = (count / project_stats["total_cases"]) * 100
        report.info(f"   {sub_suite:30}: {count:6} cases ({percentage:5.1f}%)")

    report.info("\n AUTOMATION STATUS TOTALS:")
    total_by_status = sorted(
        project_stats["by_automation_status"].items(), key=lambda x: x[1], reverse=True
    )
    for status, count in total_by_status:
        percentage = (count / project_stats["total_cases"]) * 100
        report.info(f"   {status:20}: {count:6} cases ({percentage:5.1f}%)")

    report.info("\n AUTOMATION COVERAGE TOTALS:")
    total_by_coverage = sorted(
        project_stats["by_automation_coverage"].items(),
        key=lambda x: x[1],
        reverse=True,
    )
    for coverage, count in total_by_coverage:
        percentage = (count / project_stats["total_cases"]) * 100
        report.info(f"   {coverage:20}: {count:6} cases ({percentage:5.1f}%)")


def analyze_all_suites(tr, project_id, show_detailed_cases=True):
    """Analyze all suites in the project"""
    try:
        # Get all suites in the project
        suites = get_all_suites(tr, project_id)

        # Overall project statistics
        project_stats = {
            "total_suites": len(suites),
            "total_cases": 0,
            "by_sub_test_suite": defaultdict(int),
            "by_automation_status": defaultdict(int),
            "by_automation_coverage": defaultdict(int),
            "by_status_coverage_combo": defaultdict(int),
            "suite_breakdown": [],
            "all_cases_detailed": [],
        }

        # Process each suite
        for suite in suites:
            suite_id = suite["id"]
            suite_name = suite["name"]

            op_log.info(f"Processing suite: {suite_name} (ID: {suite_id})")

            try:
                # Get all test cases for this suite
                cases = get_all_test_cases(tr, project_id, suite_id)

                # Analyze cases in this suite
                suite_stats = analyze_test_cases(cases)

                # Print suite statistics
                print_suite_statistics(
                    suite_name, suite_id, suite_stats, show_detailed_cases
                )

                # Add to project totals
                project_stats["total_cases"] += suite_stats["total_cases"]

                for sub_suite, count in suite_stats["by_sub_test_suite"].items():
                    project_stats["by_sub_test_suite"][sub_suite] += count

                for status, count in suite_stats["by_automation_status"].items():
                    project_stats["by_automation_status"][status] += count

                for coverage, count in suite_stats["by_automation_coverage"].items():
                    project_stats["by_automation_coverage"][coverage] += count

                for combo, count in suite_stats["by_status_coverage_combo"].items():
                    project_stats["by_status_coverage_combo"][combo] += count

                # Store suite info
                project_stats["suite_breakdown"].append(
                    {
                        "id": suite_id,
                        "name": suite_name,
                        "case_count": suite_stats["total_cases"],
                    }
                )

                # Add detailed cases to project-level collection
                for case in suite_stats["detailed_breakdown"]:
                    case["suite_name"] = suite_name
                    case["suite_id"] = suite_id
                    project_stats["all_cases_detailed"].append(case)

            except Exception as e:
                op_log.error(f"Error processing suite {suite_id}: {e}")
                continue

        # Print overall project summary
        print_project_summary(project_stats)

        # Print focused numerical summaries
        print_numerical_summary(project_stats)

        return project_stats

    except Exception as e:
        op_log.error(f"Error analyzing suites: {e}")
        return None


def main():
    # Configuration options
    SHOW_DETAILED_CASES = (
        True  # Set to True to show individual test case listings with IDs and titles
    )

    # Read credentials from environment
    base_url = os.environ.get("TESTRAIL_BASE_URL")
    username = os.environ.get("TESTRAIL_USERNAME")
    api_key = os.environ.get("TESTRAIL_API_KEY")

    if not all([base_url, username, api_key]):
        op_log.error("Missing TestRail credentials. Check your .env file.")
        return

    op_log.info(f"Loaded credentials for user: {username}")
    op_log.info(f"Base URL: {base_url}")

    # Initialize TestRail connection
    tr = testrail_init()

    # Analyze all suites in the project
    op_log.info(f" Starting analysis of project ID: {PROJECT_ID}...")

    project_stats = analyze_all_suites(tr, PROJECT_ID, SHOW_DETAILED_CASES)

    if project_stats:
        op_log.info("Analysis completed successfully!")

        # Print final summary
        report.info(f"\n{'=' * 80}")
        report.info("FINAL ANALYSIS COMPLETE")
        report.info(f"{'=' * 80}")
        report.info(f" Analyzed {project_stats['total_suites']} suites")
        report.info(f" Processed {project_stats['total_cases']} test cases")
        report.info(" Generated detailed statistics and breakdowns")
    else:
        op_log.error(" Analysis failed!")


if __name__ == "__main__":
    main()
