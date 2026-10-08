from dataclasses import dataclass

# The full-page chat tab. When grouping from full page, Firefox's confirmation
# card offers to put the chat tab in the group too, ticked by default
# (offerChatTab in ManageTabs.sys.mjs), so it isn't one of the scenario's tabs.
CHAT_TAB_URL = "chrome://browser/content/aiwindow/aiWindow.html"


@dataclass
class TabGroupingScenario:
    instruction: str
    pages: list[str]
    expected: list[str]
    """
    A Smart Window tab grouping request and the group it should produce.

    Pages are file names in data/smart_window_pages/, served by the
    tab_pages fixture.

    Attributes
    ----------
    instruction : str
        What the test asks Smart Window, e.g. "Group my recipe tabs".
    pages : list[str]
        Pages opened as tabs, in this order. In the sidebar the last one is
        the selected tab, which the model sees as the current page.
    expected : list[str]
        The pages that belong in the one group the request should create.
    """

    def check_grouping(self, groups: list[dict], requested: list[str]):
        """
        Assert that the tabs were grouped as this scenario expects.

        Checks Firefox before the model: tabs the model asked to group but
        that Firefox left out are a Firefox bug; a wrong choice of tabs is
        the model's (only possible when recording or running live).

        Parameters
        ----------
        groups : list[dict]
            TabBar.get_tab_groups().
        requested : list[str]
            URLs of the tabs the model's manage_tabs call asked to group.
        """
        grouped = [
            _page(url)
            for group in groups
            for url in group["urls"]
            if url != CHAT_TAB_URL
        ]
        dropped = [_page(url) for url in requested if _page(url) not in grouped]
        assert not dropped, (
            f"Firefox left out {dropped}, which manage_tabs asked to group"
        )
        assert len(groups) == 1, f"Expected 1 tab group, found {len(groups)}: {groups}"
        missing = [page for page in self.expected if page not in grouped]
        unexpected = [page for page in grouped if page not in self.expected]
        assert not (missing or unexpected), (
            f'The model grouped "{groups[0]["label"]}" with {grouped}: '
            f"missing {missing}, unexpected {unexpected}"
        )


def _page(url: str) -> str:
    return url.rsplit("/", 1)[-1]
