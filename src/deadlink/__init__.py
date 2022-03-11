from .__about__ import __version__
from ._cli import cli
from ._main import categorize_urls

__all__ = ["categorize_urls", "cli", "__version__"]
