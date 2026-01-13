import json
import os


def parse_channels(raw: str) -> list[str]:
    if not raw:
        return []

    channels = json.loads(raw)
    if not isinstance(channels, list):
        raise ValueError(
            f"Expected JSON array for channels, got {type(channels).__name__}"
        )

    return [str(c) for c in channels]


def main() -> int:
    raw = os.environ.get("SELECT_CHANNELS", "")
    channels = parse_channels(raw)

    print("Channels:", channels)

    planned = []
    if any("starfox" in c for c in channels):
        planned += ["Run-Starfox-Win (Test-Windows)", "Run-Starfox-Mac (Test-MacOS)"]
    if any("l10n" in c for c in channels):
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
