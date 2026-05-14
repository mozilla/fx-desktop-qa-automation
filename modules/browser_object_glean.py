import time

from modules.page_base import BasePage


class Glean(BasePage):
    """BOM for Glean telemetry. Executes JS in the Firefox chrome context to read metrics."""

    def _build_poll_js(self, metric_path: str) -> str:
        """
        Build the JS code for polling a Glean metric.

        Both awaits are required:
        - testFlushAllChildren() ensures child processes flush Glean data to parent
        - testGetValue() may return a Promise; without await we'd get Promise{pending}
        """
        return f"""
            const callback = arguments[arguments.length - 1];
            (async () => {{
                try {{
                    await Services.fog.testFlushAllChildren();
                    let obj = Glean;
                    for (let p of "{metric_path}".split(".")) {{
                        obj = obj[p];
                    }}
                    const value = await obj.testGetValue();
                    callback(value || []);
                }} catch(e) {{
                    callback({{ error: String(e) }});
                }}
            }})();
        """

    def _build_timeout_error_message(
        self,
        metric_path: str,
        expected: dict[str, str],
        last_result: list,
        timeout: int,
    ) -> str:
        """Build a detailed timeout error message using the closest matching event."""
        best = max(
            last_result,
            key=lambda event: sum(
                1
                for key, expected_value in expected.items()
                if event.get("extra", {}).get(key) == expected_value
            ),
            default={},
        )
        best_payload = best.get("extra", {})

        diff_lines = [
            f"Glean metric '{metric_path}' did not match after {timeout}s.",
            "",
            "Expected vs Actual:",
        ]

        for key in sorted(expected):
            expected_value = expected[key]
            actual_value = best_payload.get(key, "<missing>")
            status = "✓" if expected_value == actual_value else "✗"
            diff_lines.append(
                f"  {status} {key}: expected={expected_value!r}, actual={actual_value!r}"
            )

        diff_lines += [
            "",
            f"Last result: {last_result}",
        ]

        return "\n".join(diff_lines)

    @BasePage.context_chrome
    def poll_glean_metric(
        self,
        metric_path: str,
        expected: dict[str, str],
        timeout: int = 30,
        poll_interval: float = 0.5,
    ) -> list:
        """
        Poll a Glean metric until at least one event matches the expected payload subset.

        Useful when a flow records multiple events for the same metric, for example
        urlbar_persisted records a first urlbar event and a second urlbar_persisted event.
        Returning on the first non-empty batch would pick the wrong event.
        """
        js_code = self._build_poll_js(metric_path)
        end_time = time.time() + timeout
        last_result = []

        while time.time() < end_time:
            result = self.driver.execute_async_script(js_code)

            if isinstance(result, dict) and "error" in result:
                raise AssertionError(f"Glean JS error: {result['error']}")

            if result:
                last_result = result
                for event in result:
                    payload = event.get("extra", {})
                    if all(
                        payload.get(key) == value for key, value in expected.items()
                    ):
                        return result

            time.sleep(poll_interval)

        raise TimeoutError(
            self._build_timeout_error_message(
                metric_path,
                expected,
                last_result,
                timeout,
            )
        )
