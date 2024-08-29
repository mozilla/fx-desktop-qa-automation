from dataclasses import dataclass


@dataclass
class Bookmark:
    url: str
    name: str | None = None
    tags: str | None = None
    keyword: str | None = None
    """
    This class instantiates an AutofillAddress object that can be extended in future autofill related objects.

    Attributes
    ----------
    name : str | None
        Name of the website
    url: str | None
        URL of the website
    tags: str | None
        Tags of the bookmark
    keyword: str | None
        The keyword of the bookmark
    """
