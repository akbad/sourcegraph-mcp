import asyncio
import logging
import os
import pathlib
import signal
from typing import Any, List

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from sourcegraph_mcp.backends import SourcegraphClient, SourcegraphContentFetcher
from sourcegraph_mcp.backends.models import FormattedResult
from sourcegraph_mcp.core import PromptManager
from sourcegraph_mcp.exceptions import ContentFetchError, SearchError, ServerShutdownError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class ServerConfig:
    def __init__(self) -> None:
        # Sourcegraph instance endpoint must be set
        self.sourcegraph_endpoint = self._get_required_env_var("SRC_ENDPOINT")

        self.sse_port = int(os.getenv("MCP_SSE_PORT", "8000"))
        self.streamable_http_port = int(os.getenv("MCP_STREAMABLE_HTTP_PORT", "8080"))
        self.sourcegraph_token = os.getenv("SRC_ACCESS_TOKEN", "")  # Optional

    @staticmethod
    def _get_required_env_var(key: str) -> str:
        """Get required environment variable or raise descriptive error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value


config = ServerConfig()

server = FastMCP()

# Singleton instances created once at module load & reused for all requests
search_client = SourcegraphClient(endpoint=config.sourcegraph_endpoint, token=config.sourcegraph_token)
content_fetcher = SourcegraphContentFetcher(endpoint=config.sourcegraph_endpoint, token=config.sourcegraph_token)

# Load tool descriptions from YAML source of truth
prompt_manager = PromptManager(file_path=pathlib.Path(__file__).parent / "prompts" / "prompts.yaml")
CODESEARCH_GUIDE = prompt_manager._load_prompt("guides.codesearch_guide")
SEARCH_TOOL_DESCRIPTION = prompt_manager._load_prompt("tools.search")
SEARCH_PROMPT_GUIDE_DESCRIPTION = prompt_manager._load_prompt("tools.search_prompt_guide")
FETCH_CONTENT_DESCRIPTION = prompt_manager._load_prompt("tools.fetch_content")

# Load organization-specific guide if set
try:
    ORG_GUIDE = prompt_manager._load_prompt("guides.org_guide")
except Exception:
    ORG_GUIDE = ""


_shutdown_requested = False

def signal_handler(sig: int, frame: Any) -> None:
    """
    Handle termination signals (e.g. SIGTERM, SIGINT) for graceful shutdown.

    Activates 'drain mode': active requests complete but new requests are rejected.
    """
    global _shutdown_requested
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    _shutdown_requested = True


@server.tool(description=FETCH_CONTENT_DESCRIPTION)
def fetch_content(repo: str, path: str) -> str:
    if _shutdown_requested:
        logger.info("Shutdown in progress, declining new requests")
        return ""

    try:
        result = content_fetcher.get_content(repo, path)
        return result
    except ValueError as e:
        logger.warning(f"Error fetching content from {repo}: {str(e)}")
        raise ContentFetchError("Invalid arguments: path or repository does not exist") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching content: {e}")
        raise ContentFetchError("Error fetching content") from e


@server.tool(description=SEARCH_TOOL_DESCRIPTION)
def search(query: str) -> List[FormattedResult]:
    if _shutdown_requested:
        logger.info("Shutdown in progress, declining new requests")
        raise ServerShutdownError("Server is shutting down")

    num_results = 30

    try:
        results = search_client.search(query, num_results)
        formatted_results = search_client.format_results(results, num_results)
        return formatted_results
    except requests.exceptions.HTTPError as exc:
        logger.error(f"Search HTTP error: {exc}")
        raise SearchError(f"HTTP error during search: {exc}") from exc
    except Exception as exc:
        logger.error(f"Unexpected error during search: {exc}")
        raise SearchError(f"Unexpected error during search: {exc}") from exc


@server.tool(description=SEARCH_PROMPT_GUIDE_DESCRIPTION)
def search_prompt_guide(objective: str) -> str:
    if _shutdown_requested:
        logger.info("Shutdown in progress, declining new prompt guide requests")
        raise ServerShutdownError("Server is shutting down")

    prompt_parts = []

    if ORG_GUIDE:
        prompt_parts.append(ORG_GUIDE)
        prompt_parts.append("\n\n")

    prompt_parts.append(CODESEARCH_GUIDE)
    prompt_parts.append(
        f"\nGiven this guide create a Sourcegraph query for {objective} and call the search tool accordingly."
    )

    return "".join(prompt_parts)


async def _run_server() -> None:
    """Run the FastMCP server with both HTTP and SSE transports."""
    tasks = [
        server.run_http_async(
            transport="streamable-http",
            host="0.0.0.0",
            path="/sourcegraph/mcp",
            port=config.streamable_http_port,
        ),
        server.run_http_async(transport="sse", host="0.0.0.0", port=config.sse_port),
    ]
    await asyncio.gather(*tasks)


def main() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("Starting Sourcegraph MCP server...")
        asyncio.run(_run_server())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt (CTRL+C)")
    except Exception as exc:
        logger.error(f"Server error: {exc}")
        raise
    finally:
        logger.info("Server has shut down.")


if __name__ == "__main__":
    main()
