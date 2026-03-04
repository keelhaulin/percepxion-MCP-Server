# Percepxion MCP tools reference

This document lists all tools exposed by the Percepxion MCP server.
It is designed for quick scanning and linking from issues or PRs.

## Tool count summary

- Total tools: 23
- Source file: `src/percepxion_mcp/server.py`

## Quick usage rules

- Call `login_with_env` once per MCP server process start.
- Many actions run as jobs.
  These tools return a job group record, not the final device output.
- Use `search_job_groups` to track job progress and results.

## Summary table

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

## Job tracking pattern

Several tools create a job group.
Track that job group with `search_job_groups`.

### Example: run a CLI command

1. Run the command tool.

```json
{ "device_id": "abc-123", "command": "show version" }
```

2. Search for the job group.
The CLI tool uses `CLI_<device_id_prefix>` as its name.

```json
{ "search_string": "CLI_abc-123", "job_type": "command", "subtype": "cli" }
```

### Example: apply a saved config update

1. Save and apply.

```json
{ "device_id": "abc-123", "property_name": "ntp_server", "new_value": "10.10.10.10", "apply_now": true }
```

2. Search for the apply job.
The config apply job uses `Config_Update_<device_id_prefix>` as its name.

```json
{ "search_string": "Config_Update_abc-123", "job_type": "command", "subtype": "config" }
```

## Notes on tool names and follow ups

Some job names are short.
Prefer a unique name per action.
If you need that, add a `name` parameter to the tool and pass it through.
See `docs/adding-new-tools.md`.
