"""Plan Firefox automation branch resolution and train promotion."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from scripts.firefox_train import FirefoxTrain, resolve_train_from_artifact


RELEASE_BRANCH_RE = re.compile(r"^firefox(?P<major>\d{2,3})$")


@dataclass(frozen=True)
class BranchPlan:
    """A branch lookup result for one Firefox build."""

    action: str
    branch: str
    source_ref: str | None
    channel: str
    version: str
    reason: str


@dataclass(frozen=True)
class PromotionPlan:
    """A complete Nightly-to-Beta branch transition plan."""

    action: str
    beta_version: str
    beta_major: int
    released_major: int | None
    archive_branch: str | None
    source_ref: str | None
    target_ref: str | None
    delete_branches: tuple[str, ...]
    reason: str


def _normalize_refs(refs: list[str] | set[str]) -> set[str]:
    normalized = set()
    for ref in refs:
        ref = ref.strip()
        for prefix in ("refs/heads/", "origin/"):
            if ref.startswith(prefix):
                ref = ref.removeprefix(prefix)
        if ref:
            normalized.add(ref)
    return normalized


def _retention_deletes(
    refs: set[str],
    retention: int,
    include_branch: str | None = None,
) -> tuple[str, ...]:
    numbered_refs = set()
    for ref in refs | ({include_branch} if include_branch else set()):
        match = RELEASE_BRANCH_RE.fullmatch(ref)
        if match:
            numbered_refs.add((int(match.group("major")), ref))

    ordered = [ref for _, ref in sorted(numbered_refs, reverse=True)]
    return tuple(ordered[retention:])


def plan_branch_action(
    build: FirefoxTrain,
    existing_refs: list[str] | set[str],
    execution_channel: str | None = None,
) -> BranchPlan:
    """Resolve a build to ``nightly``, ``main``, or ``firefoxNNN``."""
    refs = _normalize_refs(existing_refs)
    normalized_channel = (execution_channel or build.channel).lower()
    if normalized_channel in {"beta", "devedition"}:
        branch = "main"
    elif normalized_channel == "rc":
        release_branch = f"firefox{build.major}"
        branch = release_branch if release_branch in refs else "main"
    elif normalized_channel == "nightly":
        branch = "nightly"
    else:
        branch = build.automation_ref
    if branch in refs:
        return BranchPlan(
            action="use",
            branch=branch,
            source_ref=None,
            channel=build.channel,
            version=build.version,
            reason="The compatible automation branch exists.",
        )

    return BranchPlan(
        action="missing",
        branch=branch,
        source_ref=None,
        channel=build.channel,
        version=build.version,
        reason=f"The required automation branch {branch!r} does not exist.",
    )


def plan_promotion(
    beta_build: FirefoxTrain,
    existing_refs: list[str] | set[str],
    retention: int = 2,
    promotion_requested: bool = False,
    released_major: int | None = None,
) -> PromotionPlan:
    """Plan bootstrap, promotion, no-op, or retention for the active trains."""
    if beta_build.channel != "beta":
        raise ValueError("Promotion planning requires a Firefox Beta build.")
    if retention < 1:
        raise ValueError("At least one numbered Firefox branch must be retained.")

    refs = _normalize_refs(existing_refs)
    if "main" not in refs:
        return PromotionPlan(
            action="blocked",
            beta_version=beta_build.version,
            beta_major=beta_build.major,
            released_major=None,
            archive_branch=None,
            source_ref=None,
            target_ref=None,
            delete_branches=(),
            reason="The required main branch does not exist.",
        )

    if "nightly" not in refs and promotion_requested:
        return PromotionPlan(
            action="blocked",
            beta_version=beta_build.version,
            beta_major=beta_build.major,
            released_major=None,
            archive_branch=None,
            source_ref=None,
            target_ref=None,
            delete_branches=(),
            reason=(
                "The nightly branch must be bootstrapped before an explicit "
                "promotion API request can be processed."
            ),
        )

    if "nightly" not in refs:
        return PromotionPlan(
            action="bootstrap",
            beta_version=beta_build.version,
            beta_major=beta_build.major,
            released_major=None,
            archive_branch=None,
            source_ref="main",
            target_ref="nightly",
            delete_branches=(),
            reason="Create the initial nightly branch from the current Beta baseline.",
        )

    is_first_beta = bool(re.search(r"b1$", beta_build.version, re.IGNORECASE))
    outgoing_major = (
        released_major if released_major is not None else beta_build.major - 1
    )
    if outgoing_major < 1 or outgoing_major >= beta_build.major:
        raise ValueError(
            "The released Firefox major must be older than the promoted Beta major."
        )

    archive_branch = f"firefox{outgoing_major}"
    if archive_branch in refs:
        return PromotionPlan(
            action="noop",
            beta_version=beta_build.version,
            beta_major=beta_build.major,
            released_major=outgoing_major,
            archive_branch=archive_branch,
            source_ref=None,
            target_ref=None,
            delete_branches=_retention_deletes(refs, retention),
            reason="This Firefox train transition was already completed.",
        )

    if not promotion_requested and not is_first_beta:
        return PromotionPlan(
            action="noop",
            beta_version=beta_build.version,
            beta_major=beta_build.major,
            released_major=outgoing_major,
            archive_branch=archive_branch,
            source_ref=None,
            target_ref=None,
            delete_branches=(),
            reason="Waiting for Beta 1 or an explicit promotion API request.",
        )

    return PromotionPlan(
        action="promote",
        beta_version=beta_build.version,
        beta_major=beta_build.major,
        released_major=outgoing_major,
        archive_branch=archive_branch,
        source_ref="nightly",
        target_ref="main",
        delete_branches=_retention_deletes(refs, retention, archive_branch),
        reason=(
            "Archive the outgoing Beta, promote nightly to main, and retain only "
            f"the newest {retention} numbered branches."
        ),
    )


def main(argv: list[str] | None = None) -> int:
    """Print a branch lookup or promotion plan as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_url", help="Firefox archive artifact/candidate URL")
    parser.add_argument(
        "--existing-ref",
        action="append",
        default=[],
        help="Existing remote branch; may be provided multiple times",
    )
    parser.add_argument(
        "--execution-channel",
        help="Workflow channel override, such as rc or devedition",
    )
    parser.add_argument(
        "--plan-promotion",
        action="store_true",
        help="Plan a Nightly-to-Beta transition instead of a branch lookup",
    )
    parser.add_argument(
        "--promotion-requested",
        action="store_true",
        help="Treat the build as an explicit promotion API event",
    )
    parser.add_argument(
        "--released-major",
        type=int,
        help="Outgoing Beta major supplied by the promotion API",
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=2,
        help="Number of firefoxNNN branches to retain (default: 2)",
    )
    args = parser.parse_args(argv)
    build = resolve_train_from_artifact(args.artifact_url)
    if args.plan_promotion:
        plan = plan_promotion(
            build,
            args.existing_ref,
            retention=args.retention,
            promotion_requested=args.promotion_requested,
            released_major=args.released_major,
        )
    else:
        plan = plan_branch_action(
            build,
            args.existing_ref,
            execution_channel=args.execution_channel,
        )
    print(json.dumps(asdict(plan)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
