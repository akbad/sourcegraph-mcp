# Sourcegraph MCP

> MCP server exposing [Sourcegraph](https://sourcegraph.com)'s AI-enhanced code search capabilities to coding agents.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 2.11.2+](https://img.shields.io/badge/FastMCP-2.11.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

***Contents:***

- [What this is](#what-this-is)
  - [Features](#features)
- [Quickstart](#quickstart)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Installing and running the server](#installing-and-running-the-server)
- [Connecting your coding agents](#connecting-your-coding-agents)
  - [Cursor](#cursor)
  - [Claude Code](#claude-code)
  - [Codex CLI](#codex-cli)
  - [Gemini CLI](#gemini-cli)
- [MCP tools](#mcp-tools)
  - [`search`](#search)
  - [`search_prompt_guide`](#search_prompt_guide)
  - [`fetch_content`](#fetch_content)
- [Development](#development)
  - [Linting and formatting](#linting-and-formatting)

## What this is

This MCP server integrates with [Sourcegraph](https://sourcegraph.com/), a universal code search platform that enables searching across multiple repositories and codebases. It provides powerful search capabilities with advanced query syntax, making it ideal for AI assistants that need to find and understand code patterns across large codebases.

> This is an actively-maintained, detached fork of [divar-ir/sourcegraph-mcp](https://github.com/divar-ir/sourcegraph-mcp).

### Features

- **Code search**: Search across codebases using Sourcegraph's powerful query language
- **Advanced query language**: Support for regex patterns, file filters, language filters, and boolean operators
- **Repository discovery**: Find repositories by name and explore their structure
- **Content fetching**: Browse repository files and directories
- **AI integration**: Designed for LLM integration with guided search prompts
- **Python 3.10+ compatible**: Fully tested and working on Python 3.10, 3.11, and 3.12+

## Quickstart

### Prerequisites

- A **Sourcegraph instance**: access to a Sourcegraph instance (i.e., either the sourcegraph.com cloud-hosted remote or a private self-hosted instance)

  > Note the Sourcegraph cloud-hosted remote offers a **free tier**: this is probably the quickest option for first-time/unfamiliar users.

- **Python 3.10+**
- **`uv`** (optional but recommended): offers easier dependency & interpreter management

### Configuration

Server configuration is done **via environment variables**. You can either: 

- Add these to a `.env` file in this repo (using [`.env.sample`](.env.sample) as a template)
- Prepend them to the server launch command

#### <ins>Required</ins> values

> [!IMPORTANT]
>
> You must set the following config values:
> 
> - `SRC_ENDPOINT`: URL pointing to the desired Sourcegraph instance (e.g., https://sourcegraph.com)

#### Optional values

| Variable | Usage |
| :--- | :--- |
| `SRC_ACCESS_TOKEN` | Auth token (for private Sourcegraph instances) |
| `MCP_SSE_PORT` | SSE server port (default: `8000`) |
| `MCP_STREAMABLE_HTTP_PORT` | HTTP server port (default: `8080`) |
| `FASTMCP_SSE_PATH` | SSE endpoint path (default: /sourcegraph/sse) |
| `FASTMCP_MESSAGE_PATH` | SSE messages endpoint path (default: /sourcegraph/messages/) |

### Installing and running the server

#### Method 1: From source using `uv` <ins>(recommended)</ins>

1. Clone the repo:

    ```bash
    git clone https://github.com/akbad/sourcegraph-mcp.git
    cd sourcegraph-mcp
    ```

2. Install dependencies

    ```bash
    uv sync
    ```

3. Run the server

    ```bash
    uv run python -m src.main
    ```

#### Method 2: From source using `pip`/`python`

1. Do either of the following:

    - Install via `pip` directly from GitHub

        ```bash
        pip install git+https://github.com/akbad/sourcegraph-mcp.git
        ```
      
    - Clone the repo source
        
        ```bash
        git clone https://github.com/akbad/sourcegraph-mcp.git
        ```

2. Install and run the server:

    ```bash
    cd sourcegraph-mcp
    pip install -e .
    python -m src.main
    ```

#### Method 3: Using a Docker container

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/akbad/sourcegraph-mcp:latest

# Or build locally
git clone https://github.com/akbad/sourcegraph-mcp.git
cd sourcegraph-mcp
docker build -t sourcegraph-mcp .

# Run the container with default ports...
docker run -p 8000:8000 -p 8080:8080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  ghcr.io/akbad/sourcegraph-mcp:latest

# ... or custom ports
docker run -p 9000:9000 -p 9080:9080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  -e MCP_SSE_PORT=9000 \
  -e MCP_STREAMABLE_HTTP_PORT=9080 \
  ghcr.io/akbad/sourcegraph-mcp:latest
```

## Connecting your coding agents

> [!NOTE]
> 
> If you customized the port using `MCP_STREAMABLE_HTTP_PORT`, update the URLs below accordingly.

### Cursor

After running the MCP server, add the following to your `.cursor/mcp.json` file:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "url": "http://localhost:8080/sourcegraph/mcp/"
    }
  }
}
```

### Claude Code

After running the MCP server, add it to Claude Code using the `claude` CLI:

```bash
claude mcp add --transport http sourcegraph --scope user \
  http://localhost:8080/sourcegraph/mcp/
```

Verify the server was added:
```bash
claude mcp list
```

### Codex CLI

After running the MCP server, add the following to your `~/.codex/config.toml`:

```toml
[mcp_servers.sourcegraph]
url = "http://localhost:8080/sourcegraph/mcp/"
transport = "http"
```

Verify the server is configured:
```bash
codex mcp list
```

### Gemini CLI

After running the MCP server, add the following to your `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "httpUrl": "http://localhost:8080/sourcegraph/mcp/"
    }
  }
}
```

Verify the server is configured:
```bash
gemini mcp list
```

## MCP tools

This server provides three powerful tools for AI assistants:

### 🔍 search

Search across codebases using Sourcegraph's advanced query syntax with support for regex, language filters, and boolean operators.

**Example queries**:
- `repo:github.com/kubernetes/kubernetes error handler`
- `lang:python class UserService`
- `file:\.go$ func SendMessage`

### 📖 search_prompt_guide

Generate a context-aware guide for constructing effective search queries based on your specific objective. This tool helps AI assistants learn how to use Sourcegraph's query syntax effectively.

**Parameters**:
- `objective`: What you're trying to find or accomplish

### 📂 fetch_content

Retrieve file contents or explore directory structures from repositories.

**Parameters**:
- `repo`: Repository path (e.g., "github.com/org/project")
- `path`: File or directory path within the repository

## Migrating from upstream

How to switch to this maintained fork if you're currently using [the upstream]([text](https://github.com/divar-ir/sourcegraph-mcp)):

> [!IMPORTANT]
> **Breaking changes:**
>
> 1. **FastMCP version**: Minimum version is now 2.11.2+ (was 2.4.0)
> 2. **Environment variables**: Add these to your `.env` file:
>    ```bash
>    FASTMCP_SSE_PATH=/sourcegraph/sse
>    FASTMCP_MESSAGE_PATH=/sourcegraph/messages/
>    ```
> 3. **Python version**: Ensure you're using Python 3.10+ (3.12+ fully supported)

### Migration steps

1. Update git remote

    ```bash
    cd /path/to/your/sourcegraph-mcp
    git remote set-url origin https://github.com/akbad/sourcegraph-mcp.git
    ```

2. Pull the latest changes

    ```bash
    git pull origin master
    ```

3. Update dependencies
    
    ```bash
    uv sync  # or: pip install --upgrade -e .
    ```

4. Add new environment variables to `.env`

    ```bash
    echo "FASTMCP_SSE_PATH=/sourcegraph/sse" >> src/.env
    echo "FASTMCP_MESSAGE_PATH=/sourcegraph/messages/" >> src/.env
    ```

5. Restart Sourcegraph MCP server
    
    ```bash
    uv run python -m src.main
    ```

## Development

### Linting and formatting

```bash
# Check code style
uv run ruff check src/

# Format code
uv run ruff format src/

# Fix auto-fixable issues
uv run ruff check --fix src/
```
