import logging

from modules.browser_object_context_menu import ContextMenu


class AboutDownloadsContextMenu(ContextMenu):
    """
    Browser object model for the context menu for right clicking a download in About:Downloads
    """

    def has_all_options_available(self) -> bool:
        for elname in [
            k for k, v in self.elements.items() if "downloadOption" in v["groups"]
        ]:
            logging.info(f"elname {elname}")
            self.element_exists(elname)
        return True
