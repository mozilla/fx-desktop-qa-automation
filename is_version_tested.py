import sys

from modules import testrail_integration as tri

if __name__ == "__main__":
    if len(sys.argv) == 2:
        channel = "Beta"
    elif len(sys.argv) > 2:
        channel = sys.argv[2]
    else:
        sys.exit("Usage: python is_version_tested.py version_number channel")
    full_version_name = f"Mozilla Firefox {sys.argv[1]}"
    plan_name = tri.get_plan_title(full_version_name, channel)
