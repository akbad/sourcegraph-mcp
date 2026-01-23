"""
Protocol definitions for search and content fetcher clients.

These function similarly to Go interfaces: any class implementing
these methods satisfies the protocol.
"""

from typing import List, Protocol, runtime_checkable

from .models import FormattedResult

# Content truncation limit for files retrieved from Sourcegraph to
#   avoid overwhelming agent context windows
MAX_FILE_SIZE = 100_000


@runtime_checkable
class SearchClientProtocol(Protocol):
    """
    Protocol for search clients.
    """

    def search(self, query: str, num: int) -> dict:
        """Execute a search query and return raw results.

        Args:
            query: The search query string
            num: Maximum number of results to return

        Returns:
            Raw search results as a dictionary
        """
        ...

    def format_results(self, results: dict, num: int) -> List[FormattedResult]:
        """Format raw search results into structured FormattedResult objects.

        Args:
            results: Raw search results from the search method
            num: Maximum number of results to format

        Returns:
            List of formatted results
        """
        ...


@runtime_checkable
class ContentFetcherProtocol(Protocol):
    """
    Protocol for content fetchers.
    """

    def get_content(self, repository: str, path: str = "", depth: int = 2, ref: str = "HEAD") -> str:
        """Get content from repository.

        Args:
            repository: Repository path (e.g., "github.com/org/project")
            path: File or directory path (e.g., "src/main.py")
            depth: Tree depth for directory listings
            ref: Git reference (branch, tag, or commit SHA)

        Returns:
            File content if path is a file, directory tree if path is a directory

        Raises:
            ValueError: If repository or path does not exist
        """
        ...
