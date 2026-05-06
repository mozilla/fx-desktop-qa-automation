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

    @BasePage.context_chrome
    def poll_glean_metric(
        self, metric_path: str, timeout: int = 30, poll_interval: float = 0.5
    ) -> list:
        """
        Poll a Glean metric via JS API until data is available.

        Calls Services.fog.testFlushAllChildren() before each check to ensure
        all child processes have flushed their Glean data to the parent.

        Arguments:
            metric_path: Dot-separated path like "serp.impression"
            timeout: Max seconds to wait
            poll_interval: Seconds between polls

        Returns:
            list: The metric events/values from testGetValue()

        Raises:
            TimeoutError: If no events are recorded within the timeout period
        """
        js_code = self._build_poll_js(metric_path)
        end_time = time.time() + timeout
        while time.time() < end_time:
            result = self.driver.execute_async_script(js_code)
            if isinstance(result, dict) and "error" in result:
                raise AssertionError(f"Glean JS error: {result['error']}")
            if result and len(result) > 0:
                return result
            time.sleep(poll_interval)

        raise TimeoutError(
            f"Glean metric '{metric_path}' had no events after {timeout}s"
        )

    def get_event_payload(self, events: list, index: int = -1) -> dict:
        """
        Extract the 'extra' payload from an event at the given index.

        Arguments:
            events: List of Glean events from poll_glean_metric()
            index: Event index (-1 for latest, 0 for first, etc.)

        Returns:
            dict: The event's extra payload, or empty dict if not found
        """
        if not events or abs(index) > len(events):
            return {}
        return events[index].get("extra", {})
