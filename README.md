# Percepxion MCP Server (FastMCP)

This repo contains a Python FastMCP server that exposes Percepxion REST APIs as MCP tools.
Run it on a workstation or utility host, then connect it to an MCP client such as Claude Desktop.

## Purpose

Percepxion already exposes a REST API.
MCP turns those endpoints into a tool catalog that an agent or chat client can call.
This repo is a practical bridge between an LLM client and Percepxion operations.

## Typical use cases

- Fleet discovery and triage from a chat UI
- Config edits on a device, then apply the change through a Percepxion job
- Clone config records from a known-good device to a target device
- Firmware baseline checks, Smart Group targeting, and staged firmware pushes
- Log collection requests, log retrieval, and access log downloads
- Audit investigations by user, keyword, and time window

## Supported device families

Percepxion supports multiple Lantronix device families. Minimum versions in the Percepxion platform guide include:

- EMG 8500: 8.2.0.0
- EMG 7500: 8.3.0.0
- SLB: 6.5.0.0
- SLC 8000: 7.6.0.1
- SpiderDuo and Spider KVM: 5.0.0.0
- LM83X and SLC hybrid: 9.6.0.0

## How it works

- The server reads credentials from `.env`.
- `login_with_env` authenticates and stores tokens in memory for this process.
- Each MCP tool maps to one or more Percepxion API endpoints.
- Every tool returns the same response envelope.

Success envelope:

```json
{
  "ok": true,
  "data": { "...": "..." },
  "status_code": 200
}
```

Error envelope:

```json
{
  "ok": false,
  "error": "Message",
  "status_code": 401,
  "details": { "...": "..." }
}
```

## Prerequisites

- Python 3.11+ (3.12 is a good target)
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
| `PERCEPXION_API_URL` | no | `https://api.gopercepxion.ai/api` | Percepxion API base URL |
| `PERCEPXION_REQUEST_TIMEOUT` | no | `45` | HTTP timeout in seconds |

## Connect an MCP client

### Claude Desktop configuration

This repo includes two examples:

- `config/claude_desktop_config.example.json` (Linux or macOS)
- `config/claude_desktop_config.wsl_windows.example.json` (Windows calling WSL)

Steps:

1. Copy one example file.
2. Replace placeholders with your local paths.
3. Restart Claude Desktop.

Keep credentials in `.env`.
Do not place secrets in the Claude config.

### First connection check

1. Start the server.
2. In your MCP client, call `login_with_env`.
3. Call `get_device_list` with `search_query` set to `*`.

If you see inventory results, the connection works.

## Tool usage rules

### Login requirement

Most tools require authentication.
Run `login_with_env` once per server process start, then retry on any 401.

### Tenant scoping

Many tools accept `tenant_id`.
Pass `tenant_id` only when your account needs it, for example a project admin view across tenants.

### Pagination

Inventory, audit, and job searches accept `limit` and `offset`.
The server clamps `limit` to a maximum of 1000.

### Date formats

Tools that accept time windows require RFC3339 timestamps.

Example:

```text
2026-03-04T00:00:00Z
```

### Asynchronous jobs

Several actions create a Percepxion job group and return a job payload.
These actions do not return final device output in the tool response.

Job-producing tools in this repo:

- `send_direct_cli_command` and `send_cli_command`
- `update_device_config` when `apply_now` is true
- `clone_device_config`
- `request_device_syslog_upload`
- `update_firmware_by_smart_group`

Track job progress with `search_job_groups`.

Example pattern:

1. Create the job (CLI, config apply, log upload request, firmware push).
2. Poll `search_job_groups` with `search_string` set to the job name prefix.
3. Review job details in the search results.

## Tool catalog

Each section lists tools, what they do, when to call them, and examples.
Examples show tool arguments as JSON. An MCP client can pass these values when invoking a tool.

### Authentication

#### login_with_env

Authenticates using `PERCEPXION_USERNAME` and `PERCEPXION_PASSWORD` from `.env`.

When to call it:
- At the start of a session.
- After any 401 response.

Example prompt:

```text
Log in to Percepxion.
```

Example arguments:

```json
{}
```

### Device inventory and discovery

#### get_device_list

Searches inventory and returns matching devices with capability details.

Key inputs:
- `search_query`: free-text search string. Default is `*` for all devices.
- `sort`: device field name. Default is `device_name`.
- `order`: `asc` or `desc`.
- `limit` and `offset` for paging.

Practical tips:
- Start with `search_query="*"` and `limit=25` during exploration.
- Raise `limit` for a fleet report, up to 1000.

Example prompt:

```text
List devices matching "slc" sorted by name.
```

Example arguments:

```json
{ "search_query": "slc", "limit": 50, "offset": 0, "sort": "device_name", "order": "asc" }
```

#### get_device_details

Fetches full device properties for one device.

Inputs:
- Provide `device_id` or `serial_num`.
- Pass `tenant_id` only when needed for scope.

Example prompt:

```text
Get details for device abc-123.
```

Example arguments:

```json
{ "device_id": "abc-123" }
```

#### get_devices_by_organization

Lists devices for a single tenant.

Inputs:
- `tenant_id` is required.
- `limit` clamps to 1000.

Example prompt:

```text
List all devices in tenant 6c2f... with a limit of 500.
```

Example arguments:

```json
{ "tenant_id": "6c2f3e7d-1111-2222-3333-444444444444", "limit": 500 }
```

### Device lifecycle

#### import_and_assign_devices

Assigns devices to a tenant. The server processes devices one-by-one and returns per-device results.

Device item fields:
- `device_id` (required)
- `device_name` (required)
- `serial_num` (required)
- `device_description` (optional)

Example prompt:

```text
Assign these devices to tenant 6c2f... and name them switch-01 and switch-02.
```

Example arguments:

```json
{
  "tenant_id": "6c2f3e7d-1111-2222-3333-444444444444",
  "devices": [
    { "device_id": "d-001", "device_name": "switch-01", "serial_num": "SN123" },
    { "device_id": "d-002", "device_name": "switch-02", "serial_num": "SN124", "device_description": "Rack 4" }
  ]
}
```

Output notes:
- `data.results` contains one entry per device with its own `ok` field.

#### unassign_devices

Unassigns one or more devices from the tenant or project association.

Example prompt:

```text
Unassign devices d-001 and d-002 from the tenant.
```

Example arguments:

```json
{ "device_ids": ["d-001", "d-002"], "tenant_id": "6c2f3e7d-1111-2222-3333-444444444444" }
```

#### remove_device_from_platform

This tool is a convenience wrapper around `unassign_devices` for a single device.
It does not delete the device record from Percepxion.

Example arguments:

```json
{ "device_id": "d-001", "tenant_id": "6c2f3e7d-1111-2222-3333-444444444444" }
```

### Smart Groups

#### automate_smart_group

Creates a Smart Group.

You can supply:
- `query`: a Smart Group query string used by Percepxion
- `device_ids`: an explicit device list

Notes:
- The tool returns the Smart Group record, including its ID. Use that ID for firmware pushes.

Example prompt:

```text
Create a Smart Group named "APAC SLC 8000" from a query.
```

Example arguments:

```json
{
  "name": "APAC SLC 8000",
  "query": "slc",
  "description": "Temporary grouping for testing",
  "temporary": true
}
```

Example arguments with device IDs:

```json
{
  "name": "Batch Set 001",
  "device_ids": ["d-001", "d-002"],
  "temporary": true
}
```

### CLI commands

#### send_direct_cli_command

Creates a Percepxion job group that runs a CLI command on one device.

Important behavior:
- The tool returns the created job group payload.
- It does not return the device command output in the same response.

Follow-up:
- Call `search_job_groups` to find the job group and inspect its state and results.

Example prompt:

```text
Run "show version" on device abc-123 and track the job.
```

Example arguments:

```json
{ "device_id": "abc-123", "command": "show version", "description": "Version check" }
```

#### send_cli_command

Alias for `send_direct_cli_command`. Keep it for older prompts and flows.

Example arguments:

```json
{ "device_id": "abc-123", "command": "show interfaces" }
```

### Device configuration

#### update_device_config

Saves config changes for a device, then triggers an apply job when `apply_now` is true.

Two input styles:

A. Single property change:
- `property_name` and `new_value`

B. Multiple changes:
- `items` as a list of objects shaped like `{ "name": "...", "value": "..." }`

Follow-up:
- When `apply_now` is true, the response includes `apply_job`. Track it with `search_job_groups`.

Example prompt:

```text
Set NTP and DNS on device abc-123, then apply the config.
```

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

Creates a configuration template from a source device, then applies it to a target device.

Inputs:
- `record_names` must match Percepxion config group names for the device type.

Follow-up:
- The tool creates a job group for the apply operation. Track it with `search_job_groups`.

Example prompt:

```text
Clone the VLAN and interface records from src-001 to tgt-002 and apply them.
```

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

Returns a small firmware summary for a device.
It calls `get_device_details` then extracts firmware fields.

Example arguments:

```json
{ "device_id": "abc-123" }
```

#### firmware_compliance_report

Compares a set of devices against an expected firmware version.
It reads `firmware_ver` from the device search results.

Inputs:
- `expected_firmware_version` is required.
- `model_filter` can narrow evaluation by model.

Example prompt:

```text
Report which SLC 8000 devices are not on 7.6.0.1.
```

Example arguments:

```json
{
  "expected_firmware_version": "7.6.0.1",
  "search_query": "slc",
  "model_filter": "SLC 8000",
  "limit": 1000
}
```

#### update_firmware_by_smart_group

Uploads a firmware file and targets one or more Smart Groups.

Inputs:
- `firmware_file_path` must exist on the same machine that runs this server.
- `smart_group_ids` is a list of Smart Group IDs.
- `content_name` and `version` label the upload inside Percepxion.
- `enable` controls activation.

Follow-up:
- Percepxion performs the rollout asynchronously. Track related jobs with `search_job_groups`.

Example prompt:

```text
Upload firmware and push it to Smart Group sg-001, then track the rollout.
```

Example arguments:

```json
{
  "firmware_file_path": "/home/user/firmware/fw-7.6.0.2.bin",
  "smart_group_ids": ["sg-001"],
  "content_name": "SLC_8000_7.6.0.2",
  "version": "7.6.0.2",
  "description": "March 2026 pilot",
  "enable": true
}
```

### Logging and monitoring

#### get_device_syslogs

Queries syslog content that has already been uploaded to Percepxion storage.

Notes:
- This tool does not trigger an upload. Use `request_device_syslog_upload` for that.

Example arguments:

```json
{ "device_id": "abc-123", "limit": 20 }
```

#### request_device_syslog_upload

Creates a job group that requests devices to upload logs.

Inputs:
- `device_ids` is required.
- `log_type` values: all, network, services, authentication, device_ports, diagnostics, general, software
- `log_level` values: error, warn, info, debug
- `from_date` and `to_date` take RFC3339 timestamps.

Follow-up:
- Track job completion with `search_job_groups`.
- Pull uploaded content with `get_device_syslogs`.

Example prompt:

```text
Request error logs from d-001 and d-002 for March 1 through March 4 UTC.
```

Example arguments:

```json
{
  "device_ids": ["d-001", "d-002"],
  "log_type": "all",
  "log_level": "error",
  "from_date": "2026-03-01T00:00:00Z",
  "to_date": "2026-03-04T00:00:00Z"
}
```

#### query_device_access_log

Queries device access log entries with pagination.

Notes:
- `limit` clamps to 1000.
- `offset` starts at 0.

Example arguments:

```json
{ "device_id": "abc-123", "log_level": "info", "limit": 200, "offset": 0 }
```

#### download_device_access_log

Downloads the complete access log content for a device.

Example arguments:

```json
{ "device_id": "abc-123", "log_level": "info" }
```

#### get_security_telemetry

Fetches telemetry statistics used for security analysis.

Inputs:
- `selected=true` returns a reduced set. Set `selected=false` for full telemetry when the API supports it.

Example arguments:

```json
{ "device_id": "abc-123", "selected": true }
```

### Audit and job tracking

#### investigate_audit_logs

Searches audit records.

Inputs:
- `search_string` filters by keyword.
- `usernames` filters by a user list.
- Omit dates to search a broad default range.

Example prompt:

```text
Show audit actions for jane.smith during the last 3 days.
```

Example arguments:

```json
{
  "usernames": ["jane.smith"],
  "from_date": "2026-03-01T00:00:00Z",
  "to_date": "2026-03-04T00:00:00Z",
  "limit": 200,
  "order": "desc"
}
```

#### investigate_user_audit_logs

Searches users and returns a summary of each user's last audit action.

Example arguments:

```json
{ "user_filter": "admin", "limit": 100, "order": "asc" }
```

#### search_job_groups

Searches job groups so you can monitor asynchronous work.

Inputs:
- `job_type` values: firmware, config, diag, command
- `subtype` values: cli, config, log, diag, organization, telemetry

Example prompt:

```text
Find recent CLI jobs for device abc-123.
```

Example arguments:

```json
{ "search_string": "CLI_", "job_type": "command", "subtype": "cli", "limit": 50 }
```

## Example workflows

These examples describe common tool sequences. They map well to agent plans and chat prompts.

### Triage one device

1. `login_with_env`
2. `get_device_list` to find the device ID
3. `get_device_details` to confirm model and status
4. `send_direct_cli_command` to create the CLI job
5. `search_job_groups` to track completion
6. `get_device_syslogs` to review recent syslog content

### Apply a config tweak

1. `login_with_env`
2. `update_device_config` with `apply_now=true`
3. `search_job_groups` using `search_string="Config_Update_"`

### Clone a baseline config

1. `login_with_env`
2. `clone_device_config`
3. `search_job_groups` with `search_string="Apply_"`

### Firmware pilot for a target set

1. `login_with_env`
2. `firmware_compliance_report` to find outliers
3. `automate_smart_group` with explicit `device_ids` for the pilot set
4. `update_firmware_by_smart_group`
5. `search_job_groups` to track rollout
6. `firmware_compliance_report` again to confirm

### Audit investigation

1. `login_with_env`
2. `investigate_user_audit_logs` to see active users
3. `investigate_audit_logs` with usernames and a time window

## Troubleshooting

- "Not authenticated" means `login_with_env` has not run in this server process.
- A 401 clears stored tokens. Run `login_with_env` again.
- Raise `PERCEPXION_REQUEST_TIMEOUT` for slow links or large downloads.
- Confirm `PERCEPXION_API_URL` when all calls fail.

## Security notes

- Treat `.env` as a secret and keep it out of git.
- Use a least-privilege Percepxion account for automation.
- The server stores auth tokens in memory only.

## Changelog

See `CHANGELOG.md`.

## License

See `LICENSE`.
