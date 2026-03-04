# Percepxion MCP Server (FastMCP)

This repo contains a Python **FastMCP** server that exposes Percepxion REST APIs as MCP tools.
It was built as a proof of concept for connecting an LLM client (for example Claude Desktop) to Percepxion.

## What you get

- A FastMCP server with **23 tools** for Percepxion (inventory, CLI, config, firmware, logs, telemetry)
- A `.env` template for credentials and API URL
- Example Claude Desktop MCP server configuration (no local user paths)
- Docs describing the available tools

## Prerequisites

- Python 3.11+ (3.12 recommended)
- Network access to your Percepxion API endpoint
- A Percepxion username and password

## Quick start (WSL or Linux)

```bash
git clone <this-repo-url>
cd percepxion-mcp-server

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and set PERCEPXION_USERNAME and PERCEPXION_PASSWORD

python percepxion_mcp.py
```

If the server starts successfully, it will run in the foreground and wait for MCP client connections.

## Environment variables

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `PERCEPXION_USERNAME` | yes | none | Percepxion login username |
| `PERCEPXION_PASSWORD` | yes | none | Percepxion login password |
| `PERCEPXION_API_URL` | no | `https://api.gopercepxion.ai/api` | Base API URL |
| `PERCEPXION_REQUEST_TIMEOUT` | no | `45` | Request timeout in seconds |

## Claude Desktop configuration

Claude Desktop reads its MCP server config from a JSON file.
This repo includes an example at `config/claude_desktop_config.example.json`.

1. Copy the example file and edit it for your system.
2. Update the command and args to point to your Python interpreter and this repo path.
3. Restart Claude Desktop.

Notes:
- On Windows, the cleanest pattern is to run the server inside WSL and call it from Claude Desktop using `wsl.exe`.
- Avoid putting secrets in the Claude config. Put secrets in `.env`.

## Tool reference

See `docs/TOOLS.md` for the complete list of tools and parameters.

## Security

- Treat `.env` as a secret. Do not commit it.
- Prefer creating a Percepxion account with least privilege for automation use.
- This server stores auth tokens in memory only for the running process.

## License

Internal use. Add a formal license file if you plan external distribution.


## Changelog

See `CHANGELOG.md`.

## License

See `LICENSE`.
