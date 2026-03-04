# Percepxion MCP Server (FastMCP)

This repo contains a Python FastMCP server that exposes Percepxion REST APIs as MCP tools.
Run it on your workstation or a small utility host.
Connect it to an MCP client such as Claude Desktop.

## Purpose

Percepxion already has a REST API.
MCP turns that API into a tool catalog that an MCP client can call.
This lets you drive Percepxion tasks from a chat UI or an agent workflow.

## Common use cases

- Inventory discovery and triage
- Run CLI commands on a device, then pull logs for the same device
- Apply small config edits, then push them to the device
- Clone config records from a known good device to a target device
- Check firmware compliance across a fleet
- Push firmware to a Smart Group and track job progress
- Pull audit history for a user or time window

## How it works

- The server runs locally and reads credentials from `.env`.
- `login_with_env` authenticates and stores tokens in memory for this process.
- Each tool maps to one or more Percepxion API endpoints.
- Tool responses use a consistent envelope.

Response envelope:

```json
{
  "ok": true,
  "data": { "...": "..." },
  "status_code": 200
}
```

Failed response envelope:

```json
{
  "ok": false,
  "error": "...",
  "status_code": 401,
  "details": { "...": "..." }
}
```

## Percepxion MCP tools reference

Document docs/tools.md lists all tools exposed by the Percepxion MCP server.
It is designed for quick scanning and linking from issues or PRs.

## Tool count summary

- Total tools: 23
- Source file: `src/percepxion_mcp/server.py`

## Quick Tool usage rules

- Call `login_with_env` once per MCP server process start.
- Many actions run as jobs.
  These tools return a job group record, not the final device output.
- Use `search_job_groups` to track job progress and results.

## Tools Summary table

| Category | Tool | Returns final data | Primary API endpoint(s) | Follow up |
| --- | --- | --- | --- | --- |
| Authentication | `login_with_env` | Yes | `POST /v2/user/login` | None |
| Inventory | `get_device_list` | Yes | `POST /v3/device/search` | None |
| Inventory | `get_device_details` | Yes | `POST /v3/device/get` | None |
| Inventory | `get_devices_by_organization` | Yes | `POST /v3/device/search` | None |
| Lifecycle | `import_and_assign_devices` | Yes | `POST /v3/device/assign` | None |
| Lifecycle | `unassign_devices` | Yes | `POST /v3/device/unassign` | None |
| Lifecycle | `remove_device_from_platform` | Yes | `POST /v3/device/unassign` | None |
| Smart Groups | `automate_smart_group` | Yes | `POST /v3/device/smartgroup/create` | None |
| CLI | `send_direct_cli_command` | No | `POST /v1/job/jobgroup/create` | `search_job_groups` |
| CLI | `send_cli_command` | No | Wrapper for `send_direct_cli_command` | `search_job_groups` |
| Config | `update_device_config` | No | `POST /v1/telemetry/config/save` then `POST /v1/job/jobgroup/create` | `search_job_groups` |
| Config | `clone_device_config` | No | `POST /v1/telemetry/template/create` then `POST /v1/job/jobgroup/create` | `search_job_groups` |
| Firmware | `get_device_firmware_status` | Yes | `POST /v3/device/get` | None |
| Firmware | `firmware_compliance_report` | Yes | `POST /v3/device/search` | None |
| Firmware | `update_firmware_by_smart_group` | No | `POST /v3/content/create` (multipart) | `search_job_groups` |
| Logs | `request_device_syslog_upload` | No | `POST /v1/job/jobgroup/create` | `search_job_groups` |
| Logs | `get_device_syslogs` | Yes | `POST /v1/storage/file/content/query` | None |
| Logs | `query_device_access_log` | Yes | `POST /v1/storage/file/devicelog/query-by-id` | None |
| Logs | `download_device_access_log` | Yes | `POST /v1/storage/file/devicelog/download` | None |
| Security | `get_security_telemetry` | Yes | `POST /v1/telemetry/stat/view` | None |
| Audit | `investigate_audit_logs` | Yes | `POST /v1/audit/search` | None |
| Audit | `investigate_user_audit_logs` | Yes | `POST /v1/audit/user/search` | None |
| Jobs | `search_job_groups` | Yes | `POST /v1/job/jobgroup/search` | None |

## Prerequisites

- Python 3.11+ (3.12 recommended)
- Network access to your Percepxion API base URL
- A Percepxion username and password

## Deploy and run

### Quick start on Linux or WSL

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

The server runs in the foreground and waits for MCP client connections.

### Docker (optional)

```bash
docker build -t percepxion-mcp-server .
docker run --rm -it --env-file .env percepxion-mcp-server
```

### Environment variables

| Variable | Required | Default | Meaning |
| --- | --- | --- | --- |
| `PERCEPXION_USERNAME` | yes | none | Percepxion login username |
| `PERCEPXION_PASSWORD` | yes | none | Percepxion login password |
| `PERCEPXION_API_URL` | yes | `https://api.gopercepxion.ai/api` | Percepxion API base URL |
| `PERCEPXION_REQUEST_TIMEOUT` | no | `45` | HTTP timeout in seconds |

## Connect an MCP client

### Claude Desktop configuration

This repo includes two examples:

- `config/claude_desktop_config.example.json` (Linux or macOS)
- `config/claude_desktop_config.wsl_windows.example.json` (Windows calling WSL)

Steps:

1. Copy the example file.
2. Replace placeholders with your local paths.
3. Restart Claude Desktop.

Keep credentials in `.env`.
Do not place secrets in the Claude config.

### First connection check

1. Start the server.
2. In your MCP client, call `login_with_env`.
3. Run `get_device_list` with `search_query` set to `*`.

## Tool catalog

### Additional docs

- `docs/tools.md` has a summary table and job tracking patterns.
- `docs/adding-new-tools.md` covers tool development conventions.
- `docs/claude-example.prompt` is a starter prompt for Claude Desktop.


Most tools require `login_with_env` first.
Log and job tools accept date ranges in RFC3339 format.

Example RFC3339 timestamp:

```text
2026-03-04T00:00:00Z
```

### Authentication

#### login_with_env

Authenticate using `PERCEPXION_USERNAME` and `PERCEPXION_PASSWORD` from `.env`.

Example prompt:

```text
Log in to Percepxion.
```

### Device inventory and discovery

#### get_device_list

Search devices and return matching inventory details.

Key parameters:

- `search_query` (default `*`)
- `limit` and `offset` for pagination
- `sort` and `order` for sorting
- `tenant_id` to scope to an organization

Example prompt:

```text
List all devices sorted by device_name.
```

Example arguments:

```json
{ "search_query": "*", "limit": 50, "sort": "device_name", "order": "asc" }
```

#### get_device_details

Get full device properties by `device_id` or `serial_num`.

Example arguments:

```json
{ "device_id": "abc-123" }
```

#### get_devices_by_organization

List all devices assigned to a tenant.

Example arguments:

```json
{ "tenant_id": "org-456", "limit": 200 }
```

### Device lifecycle

#### import_and_assign_devices

Assign devices to a tenant.
Each device item needs `device_id`, `device_name`, and `serial_num`.

Example arguments:

```json
{
  "tenant_id": "org-456",
  "devices": [
    { "device_id": "d-001", "device_name": "switch-01", "serial_num": "SN123" },
    { "device_id": "d-002", "device_name": "switch-02", "serial_num": "SN124" }
  ]
}
```

#### unassign_devices

Remove one or more devices from their current tenant assignment.

Example arguments:

```json
{ "device_ids": ["d-001", "d-002"], "tenant_id": "org-456" }
```

#### remove_device_from_platform

Convenience wrapper for unassigning a single device.

Example arguments:

```json
{ "device_id": "abc-123" }
```

### Smart Groups

#### automate_smart_group

Create a Smart Group using a query string or an explicit list of device IDs.

Example arguments with a query:

```json
{ "name": "Building A Switches", "query": "location:building-a AND type:switch" }
```

Example arguments with explicit device IDs:

```json
{ "name": "Batch Update Set", "device_ids": ["d-001", "d-002"], "temporary": true }
```

### CLI commands

#### send_direct_cli_command

Create a CLI job group that runs a command on one device.
Use `search_job_groups` to track completion.

Example arguments:

```json
{ "device_id": "abc-123", "command": "show version" }
```

#### send_cli_command

Alias for `send_direct_cli_command`.
Keep it for older workflows.

### Device configuration

#### update_device_config

Save config items for a device, then optionally apply them.

Example arguments for a single property:

```json
{ "device_id": "abc-123", "property_name": "dns_server", "new_value": "8.8.8.8", "apply_now": true }
```

Example arguments for multiple items:

```json
{
  "device_id": "abc-123",
  "items": [
    { "name": "dns_server", "value": "8.8.8.8" },
    { "name": "ntp_server", "value": "time.google.com" }
  ],
  "apply_now": true
}
```

#### clone_device_config

Create a template from a source device, then apply it to a target device.

Example arguments:

```json
{
  "source_device_id": "src-001",
  "target_device_id": "tgt-002",
  "record_names": ["vlan", "interfaces"],
  "template_name": "Baseline_Template"
}
```

### Firmware management

#### get_device_firmware_status

Return a firmware summary for one device.

Example arguments:

```json
{ "device_id": "abc-123" }
```

#### firmware_compliance_report

Compare device firmware against an expected version.

Example arguments:

```json
{ "expected_firmware_version": "7.2.1", "search_query": "*", "limit": 1000 }
```

#### update_firmware_by_smart_group

Upload a firmware file and target one or more Smart Groups.
The firmware file path must exist on the machine running the server.

Example arguments:

```json
{
  "firmware_file_path": "/home/user/firmware/fw-7.2.1.bin",
  "smart_group_ids": ["sg-001"],
  "content_name": "fw-7.2.1",
  "version": "7.2.1",
  "description": "March 2026 baseline",
  "enable": true
}
```

### Logging and monitoring

#### get_device_syslogs

Query syslog content that already exists in Percepxion storage.

Example arguments:

```json
{ "device_id": "abc-123", "limit": 20 }
```

#### request_device_syslog_upload

Trigger a job that uploads logs from one or more devices.
Use RFC3339 timestamps for `from_date` and `to_date`.

Example arguments:

```json
{
  "device_ids": ["d-001", "d-002"],
  "log_level": "error",
  "from_date": "2026-03-01T00:00:00Z",
  "to_date": "2026-03-04T00:00:00Z"
}
```

#### query_device_access_log

Query access log entries with pagination.

Example arguments:

```json
{ "device_id": "abc-123", "log_level": "info", "limit": 200, "offset": 0 }
```

#### download_device_access_log

Download the complete access log content for one device.

Example arguments:

```json
{ "device_id": "abc-123", "log_level": "info" }
```

#### get_security_telemetry

Fetch security-relevant telemetry stats.

Example arguments:

```json
{ "device_id": "abc-123", "selected": true }
```

### Audit and job tracking

#### investigate_audit_logs

Search platform audit records.
If you omit dates, the tool searches a broad default range.

Example arguments:

```json
{
  "usernames": ["jane.smith"],
  "from_date": "2026-03-01T00:00:00Z",
  "to_date": "2026-03-04T00:00:00Z",
  "limit": 200
}
```

#### investigate_user_audit_logs

Search users and show the last recorded audit action per user.

Example arguments:

```json
{ "user_filter": "admin", "limit": 100 }
```

#### search_job_groups

Search job groups to track async operations.

Example arguments:

```json
{ "search_string": "Config_Update_", "job_type": "command", "limit": 50 }
```

## Troubleshooting

- "Not authenticated" errors mean you need to run `login_with_env`.
- A `401` response clears the stored token. Run `login_with_env` again.
- Raise `PERCEPXION_REQUEST_TIMEOUT` for slow links or large log downloads.
- Check `PERCEPXION_API_URL` if all calls fail.

## Security notes

- Treat `.env` as a secret. Do not commit it.
- Use a least-privilege Percepxion account for automation.
- The server stores auth tokens in memory only.

## Changelog

See `CHANGELOG.md`.

## License

See `LICENSE`.
