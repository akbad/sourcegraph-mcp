"""Implementations of Sourcegraph search and content fetching clients."""

from .content import SourcegraphContentFetcher
from .search import SourcegraphClient

# re-export classes for cleaner imports outside of backends/ dir:
#   note only these 2 classes will be exported if a file has
#   `from sourcegraph_mcp.backends import *`
__all__ = ["SourcegraphClient", "SourcegraphContentFetcher"]
