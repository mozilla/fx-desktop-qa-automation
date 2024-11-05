import os
import platform
from subprocess import check_output

from modules import testrail_integration as tri


def reportable():
    """Return true if we should report to TestRail"""

    sys_platform = platform.system()
    version = check_output([os.environ.get("FX_EXECUTABLE"), "--version"]).decode()
    if not os.environ.get("TESTRAIL_REPORT"):
        return False

    # Find the correct test plan
    tr_session = tri.testrail_init()
    first_half, second_half = version.split(".")
    channel = "Beta" if "b" in second_half else "Release"
    if "Nightly" in first_half:
        channel = "Nightly"

    major_version = " ".join(first_half.split(" ")[1:])
    major_number = major_version.split(" ")[-1]
    major_milestone = tr_session.matching_milestone(TESTRAIL_FX_DESK_PRJ, major_version)
    if not major_milestone:
        logging.warning("Reporting: Could not find matching milestone.")
        return False

    channel_milestone = tr_session.matching_submilestone(
        major_milestone, f"{channel} {major_number}"
    )
    if not channel_milestone:
        logging.warning(
            f"Reporting: Could not find matching submilestone for {channel} {major_number}"
        )
        return False

    this_plan = tr_session.matching_plan_in_milestone(
        TESTRAIL_FX_DESK_PRJ,
        channel_milestone.get("id"),
    )
    if not this_plan:
        return True

    platform = "MacOS" if sys_platform == "Darwin" else sys_platform

    plan_entries = this_plan.get("entries")
    covered_suites = 0
    for entry in plan_entries:
        for run_ in entry.get("runs"):
            if platform in run_.get("config"):
                covered_suites += 1

    num_suites = len([d for d in os.listdir("tests") if os.path.isdir(d)])

    return covered_suites > (num_suites - SUITE_COVERAGE_TOLERANCE)
