from typing import List, Protocol, runtime_checkable

from .models import FormattedResult


@runtime_checkable
class SearchClientProtocol(Protocol):
    """
    Protocol defining the interface for search clients.

    This functions similarly to Go interfaces: any class
    implementing these methods satisfies the protocol.
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
