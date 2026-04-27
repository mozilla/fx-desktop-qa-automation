import json
import os


def parse_test_types(raw: str) -> list[str]:
    if not raw:
        return []

    test_types = json.loads(raw)
    if not isinstance(test_types, list):
        raise ValueError(
            f"Expected JSON array for channels, got {type(test_types).__name__}"
        )

    return [str(c) for c in test_types]


def main() -> int:
    raw = os.environ.get("SELECT_CHANNELS", "")
    test_types = parse_test_types(raw)

    print("Test Types:", test_types)

    planned = []
    if any("starfox" in t for t in test_types):
        planned += ["Run-Starfox-Win (Test-Windows)", "Run-Starfox-Mac (Test-MacOS)"]
    if any("l10n" in c for c in test_types):
        planned += [
            "Run-L10n-Win (L10n-Windows)",
            "Run-L10n-Mac (L10n-MacOS)",
            "Run-L10n-Linux (L10n-Linux)",
        ]

    if not planned:
        print("No jobs selected by channels.")
    else:
        print("Planned jobs (no workflows executed):")
        for p in planned:
            print(" -", p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
