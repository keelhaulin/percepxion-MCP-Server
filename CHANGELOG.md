# Changelog

## Unreleased

## 0.3.0 - 2026-03-23

### Added
- `list_tenants` tool — list organizations visible to the current user; needed to discover `tenant_id` values for scoped operations
- `create_smart_group` tool — canonical replacement for `automate_smart_group` with clearer naming and expanded docstring
- `PERCEPXION_FIRMWARE_DIR` env var — when set, restricts `update_firmware_by_smart_group` to files in the specified directory
- CLI command audit logging — `send_direct_cli_command` now logs device ID and command string to stderr for audit purposes

### Changed
- `automate_smart_group` is now a deprecated alias for `create_smart_group`; existing workflows continue to function
- `send_cli_command` docstring updated to mark it as deprecated in favor of `send_direct_cli_command`
- `update_firmware_by_smart_group` uses `Path.resolve()` to normalize paths before directory restriction check
- `docs/tools.md` — updated job tracking examples to reflect timestamp-based job names; added deprecated aliases table; added firmware compliance + update workflow example
- README rewritten — added Percepxion product context, expanded security section, added Claude Code connection instructions, restructured tool reference tables, added troubleshooting table

## 0.2.0 - 2026-03-23

### Added
- Stderr logging via Python `logging` module — auth events, API errors, and request failures are now visible when debugging
- Unix timestamp suffix on CLI, config, and syslog job names to prevent name collisions when multiple jobs target the same device

### Changed
- Dependency versions pinned in `requirements.txt`: `fastmcp>=3.1.0,<4.0`, `requests>=2.32.0,<3.0`, `python-dotenv>=1.2.0,<2.0`

## 0.1.0 - 2026-03-04

- Initial repo packaging of the Percepxion FastMCP server PoC
