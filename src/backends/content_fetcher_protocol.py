from typing import Protocol, runtime_checkable

# Content truncation limit for files retrieved from Sourcegraph to
#   avoid overwhelming agent context windows
MAX_FILE_SIZE = 100_000


@runtime_checkable
class ContentFetcherProtocol(Protocol):
    """
    Protocol defining the interface for content fetchers.

    This functions similarly to Go interfaces: any class
    implementing these methods satisfies the protocol.
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
