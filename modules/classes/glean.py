class GleanAssertionError(AssertionError):
    """Custom error for Glean assertion failures with detailed diff output."""

    def __init__(self, message: str, expected: dict, actual: dict | None):
        if not isinstance(expected, dict):
            raise TypeError("expected must be a dict")
        if actual is not None and not isinstance(actual, dict):
            raise TypeError("actual must be a dict")

        self.expected = expected or {}
        self.actual = actual or {}

        exp_keys = set(self.expected.keys())
        act_keys = set(self.actual.keys())

        missing = sorted(exp_keys - act_keys)
        unexpected = sorted(act_keys - exp_keys)
        all_keys = sorted(exp_keys | act_keys)

        diff_lines = [message, "", "Expected vs Actual:"]
        for key in all_keys:
            exp_val = self.expected.get(key, "<missing>")
            act_val = self.actual.get(key, "<missing>")
            status = "✓" if exp_val == act_val else "✗"
            diff_lines.append(
                f"  {status} {key}: expected={exp_val!r}, actual={act_val!r}"
            )

        if missing:
            diff_lines += ["", f"Missing keys in actual: {missing}"]
        if unexpected:
            diff_lines += ["", f"Unexpected keys in actual: {unexpected}"]

        super().__init__("\n".join(diff_lines))


class GleanAsserts:
    """Static helper for Glean event assertions."""

    @staticmethod
    def assert_payload(
        metric: str,
        events: list,
        expected: dict,
        index: int = -1,
    ) -> dict:
        """
        Assert that a Glean event payload contains expected values (subset match).

        Arguments:
            metric: Metric name (for error messages)
            events: List of Glean events from poll_glean_metric()
            expected: Dict of expected key-value pairs
            index: Which event to check (-1 for latest)

        Returns:
            dict: The actual payload

        Raises:
            GleanAssertionError: If payload doesn't match
            AssertionError: If no events recorded
        """
        if not events:
            raise AssertionError(f"No {metric} events recorded")

        if not (-len(events) <= index < len(events)):
            raise AssertionError(
                f"{metric}: event index {index} out of range (have {len(events)} events)"
            )

        actual = events[index].get("extra", {})

        # Check for mismatches (subset matching)
        for key, expected_val in expected.items():
            if actual.get(key) != expected_val:
                actual_subset = {k: actual.get(k, "<missing>") for k in expected}
                raise GleanAssertionError(
                    f"{metric}[{index}]: payload mismatch",
                    expected,
                    actual_subset,
                )

        return actual
