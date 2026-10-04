"""Websites as CREAM keeps them: the bare domain ("wolt.com"). Pure module."""

import re

WEBSITE_MAX = 255
_DOMAIN = re.compile(r"^(?=.{1,255}$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$")


class InvalidWebsiteError(ValueError):
    def __init__(self, text: str):
        super().__init__(f"{text} isn't a website, e.g. wolt.com")


def is_domain(text: str) -> bool:
    return bool(_DOMAIN.match(text))


def website_domain(text: str) -> str:
    """The domain of what the user typed: "https://www.Wolt.com/el/" and "wolt.com" both give "wolt.com"."""
    domain = text.strip().casefold()
    domain = re.sub(r"^[a-z]+://", "", domain).split("/")[0].split("?")[0].removeprefix("www.")
    if not is_domain(domain):
        raise InvalidWebsiteError(text.strip())
    return domain
