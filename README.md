# Sourcegraph MCP server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 2.11.2+](https://img.shields.io/badge/FastMCP-2.11.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

A Model Context Protocol (MCP) server that provides AI-enhanced code search capabilities using [Sourcegraph](https://sourcegraph.com).

## Table of contents

- [Table of contents](#table-of-contents)
- [Overview](#overview)
  - [About this fork](#about-this-fork)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Using UV (recommended)](#using-uv-recommended)
  - [Using pip](#using-pip)
  - [Using Docker](#using-docker)
- [Configuration](#configuration)
  - [Required environment variables](#required-environment-variables)
  - [Optional environment variables](#optional-environment-variables)
- [Usage with AI tools](#usage-with-ai-tools)
  - [Cursor](#cursor)
  - [Claude Code](#claude-code)
  - [Codex CLI](#codex-cli)
  - [Gemini CLI](#gemini-cli)
- [MCP tools](#mcp-tools)
  - [🔍 search](#-search)
  - [📖 search\_prompt\_guide](#-search_prompt_guide)
  - [📂 fetch\_content](#-fetch_content)
- [Migrating from upstream](#migrating-from-upstream)
  - [Migration steps](#migration-steps)
- [Development](#development)
  - [Linting and formatting](#linting-and-formatting)

## Overview

This MCP server integrates with Sourcegraph, a universal code search platform that enables searching across multiple repositories and codebases. It provides powerful search capabilities with advanced query syntax, making it ideal for AI assistants that need to find and understand code patterns across large codebases.

### About this fork

This is an actively maintained fork of [divar-ir/sourcegraph-mcp](https://github.com/divar-ir/sourcegraph-mcp), created to patch upstream bugs and maintain an actively supported version of the Sourcegraph MCP server.

> [!NOTE] 
> ***Key additions vs. upstream:***
> 
> - **Python 3.12+ support** (compatible with 3.10+)
> - Functional package structure
> - **Tunable config via env vars**, rather than hardcoded paths
> - **FastMCP dependency upgraded to ≥2.11.2** (to integrate patches)
> 
>     - Updated to **decorator-based tool registration** (to conform to new version & for convenience)

## Features

- **Code search**: Search across codebases using Sourcegraph's powerful query language
- **Advanced query language**: Support for regex patterns, file filters, language filters, and boolean operators
- **Repository discovery**: Find repositories by name and explore their structure
- **Content fetching**: Browse repository files and directories
- **AI integration**: Designed for LLM integration with guided search prompts
- **Python 3.12+ compatible**: Fully tested and working on Python 3.10, 3.11, and 3.12+

## Prerequisites

- **Sourcegraph Instance**: Access to a Sourcegraph instance (either sourcegraph.com or self-hosted)
- **Python 3.10+**: Required for running the MCP server (Python 3.12+ fully supported)
- **uv** (optional): Modern Python package manager for easier dependency management

## Installation

### Using UV (recommended)

```bash
# Clone the repository
git clone https://github.com/akbad/sourcegraph-mcp.git
cd sourcegraph-mcp

# Install dependencies
uv sync

# Run the server
uv run python -m src.main
```

### Using pip

```bash
# Install directly from GitHub
pip install git+https://github.com/akbad/sourcegraph-mcp.git

# Or clone and install locally
git clone https://github.com/akbad/sourcegraph-mcp.git
cd sourcegraph-mcp
pip install -e .

# Run the server
python -m src.main
```

### Using Docker

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/akbad/sourcegraph-mcp:latest

# Or build locally
git clone https://github.com/akbad/sourcegraph-mcp.git
cd sourcegraph-mcp
docker build -t sourcegraph-mcp .

# Run the container with default ports
docker run -p 8000:8000 -p 8080:8080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  ghcr.io/akbad/sourcegraph-mcp:latest

# Or run with custom ports
docker run -p 9000:9000 -p 9080:9080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  -e MCP_SSE_PORT=9000 \
  -e MCP_STREAMABLE_HTTP_PORT=9080 \
  ghcr.io/akbad/sourcegraph-mcp:latest
```

## Configuration

### Required environment variables

- `SRC_ENDPOINT`: Sourcegraph instance URL (e.g., https://sourcegraph.com)

### Optional environment variables

- `SRC_ACCESS_TOKEN`: Authentication token for private Sourcegraph instances
- `MCP_SSE_PORT`: SSE server port (default: 8000)
- `MCP_STREAMABLE_HTTP_PORT`: HTTP server port (default: 8080)
- `FASTMCP_SSE_PATH`: SSE endpoint path (default: /sourcegraph/sse)
- `FASTMCP_MESSAGE_PATH`: SSE messages endpoint path (default: /sourcegraph/messages/)

## Usage with AI tools

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
      "transport": "http",
      "url": "http://localhost:8080/sourcegraph/mcp/"
    }
  }
}
```

Verify the server is configured:
```bash
gemini mcp list
```

> **Note:** If you customized the port using `MCP_STREAMABLE_HTTP_PORT`, update the URLs above accordingly.

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
