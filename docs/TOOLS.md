# Percepxion MCP tools

Here is a complete guide to all 23 Percepxion tools available, organized by category:
##  Authentication
login_with_env
Authenticates with Percepxion using credentials stored in your environment variables (PERCEPXION_USERNAME and PERCEPXION_PASSWORD). This is typically the first step before using any other tools.
When to use: Run this at the start of a session or if you receive authentication errors.
##  Device Inventory & Discovery
get_device_list
Searches your device inventory and returns matching devices with full details.
Parameters:
search_query – Filter expression (default: * for all devices)
sort / order – Sort field and direction (asc/desc)
limit / offset – Pagination controls
tenant_id (optional) – Scope to a specific tenant
Example use: "Show me all devices sorted by name" or "Find all devices matching 'router'."
get_device_details
Retrieves full properties for a single device by its ID or serial number.
Parameters:
device_id or serial_num – Provide at least one
tenant_id (optional)
Example use: "Get all details for device ID abc-123."
get_devices_by_organization
Lists all devices assigned to a specific tenant/organization.
Parameters:
tenant_id (required)
limit – Max results to return (default: 100)
Example use: "Show all devices belonging to tenant org-456."
##  Device Configuration
update_device_config
Saves configuration changes to a device and optionally applies them immediately.
Parameters:
device_id (required)
property_name + new_value – For a single property change
items – Array of {property: value} objects for bulk changes
apply_now – Whether to push changes immediately (default: true)
tenant_id (optional)
Example use: "Update the NTP server setting on device abc-123."
clone_device_config
Copies a configuration template from one device and applies it to another.
Parameters:
source_device_id (required) – The device to copy config from
target_device_id (required) – The device to apply config to
record_names (required) – List of config record names to clone
template_name – Name for the created template (default: Cloned_Template)
tenant_id (optional)
Example use: "Clone the VLAN configuration from Device A to Device B."
🖥️ CLI Commands
send_direct_cli_command
Sends a CLI command directly to a single device and returns the output.
Parameters:
device_id (required)
command (required) – The CLI command string to execute
description (optional) – Label for audit/logging purposes
Example use: "Run show interfaces on device abc-123."
send_cli_command
A backward-compatible alias for send_direct_cli_command. Works identically with the same parameters (device_id, command).
When to use: Use send_direct_cli_command for new workflows; this alias exists for legacy compatibility.
🔄 Firmware Management
get_device_firmware_status
Retrieves the current firmware version and state for a specific device.
Parameters:
device_id (required)
tenant_id (optional)
Example use: "What firmware version is device abc-123 running?"
firmware_compliance_report
Compares firmware versions across your entire fleet against an expected/target version and reports compliance.
Parameters:
expected_firmware_version (required) – The version all devices should be on
model_filter (optional) – Limit to a specific device model
search_query – Filter devices (default: *)
limit – Max devices to check (default: 1000)
tenant_id (optional)
Example use: "Which devices are NOT on firmware version 7.2.1?"
update_firmware_by_smart_group
Uploads a firmware file and targets one or more Smart Groups for update.
Parameters:
firmware_file_path (required) – Local path to the firmware file
content_name (required) – Name for this firmware package
version (required) – Version string (e.g., 7.2.1)
smart_group_ids (required) – List of Smart Group IDs to target
description (optional)
enable – Activate immediately (default: true)
tenant_id (optional)
Example use: "Push firmware 7.2.1 to all devices in Smart Group sg-001."
🗂️ Smart Groups
automate_smart_group
Creates a Smart Group using either a dynamic query or an explicit list of device IDs.
Parameters:
name (required) – Group name
query – Dynamic filter expression
device_ids – Explicit list of device IDs to include
description (optional)
temporary – Mark as a temporary group (default: false)
tenant_id (optional)
Example use: "Create a Smart Group for all devices in Building A" or "Create a temporary group with these 5 specific device IDs."
📥 Device Lifecycle
import_and_assign_devices
Assigns (onboards) devices to a Percepxion tenant or project.
Parameters:
devices (required) – Array of device objects, each with device_id, device_name, and serial_num
tenant_id (optional)
Example use: "Onboard three new switches into the production tenant."
unassign_devices
Removes one or more devices from their current tenant/project assignment.
Parameters:
device_ids (required) – List of device IDs to unassign
tenant_id (optional)
Example use: "Unassign these devices before reassigning them to a different project."
remove_device_from_platform
Fully removes a single device from the Percepxion platform entirely.
Parameters:
device_id (required)
tenant_id (optional)
Example use: "Decommission device abc-123 and remove it from Percepxion."
##  Logging & Monitoring
get_device_syslogs
Queries syslog files that have already been uploaded to Percepxion for a device.
Parameters:
device_id (required)
limit – Number of log entries to return (default: 10)
Example use: "Show me the latest syslogs for device abc-123."
request_device_syslog_upload
Triggers a job to upload syslog files from one or more devices to Percepxion.
Parameters:
device_ids (required) – List of device IDs
from_date / to_date – Date range in RFC3339 format
log_level – Severity level (default: info)
log_type – Type of log (default: all)
tenant_id (optional)
Example use: "Upload the last 24 hours of error-level syslogs from these devices."
query_device_access_log
Fetches access log entries for a device with pagination support.
Parameters:
device_id (required)
log_level – Severity filter (default: info)
limit / offset – Pagination controls
Example use: "Show the last 200 access log entries for device abc-123."
download_device_access_log
Downloads the complete access log for a device as full content (not paginated).
Parameters:
device_id (required)
log_level – Severity filter (default: info)
Example use: "Download the full access log for device abc-123 for offline review."
get_security_telemetry
Retrieves security-relevant telemetry statistics for a specific device.
Parameters:
device_id (required)
selected – Filter to selected telemetry stats (default: true)
tenant_id (optional)
Example use: "Pull security telemetry for device abc-123 to check for anomalies."
🔍 Audit & Job Tracking
investigate_audit_logs
Searches detailed audit records across the platform.
Parameters:
search_string – Keyword filter
usernames – Filter by specific user(s)
from_date / to_date – Date range (defaults to all-time if omitted)
sort / order – Sort field and direction
limit / offset – Pagination controls
tenant_id (optional)
Example use: "Show all audit events by user john.doe in the last 7 days."
investigate_user_audit_logs
Searches user records and surfaces a summary of each user's last audit action.
Parameters:
user_filter – Partial username or email to match
sort / order – Sort field and direction
limit / offset – Pagination controls
tenant_id (optional)
Example use: "Which users have been active recently, and what was each person's last action?"
search_job_groups
Monitors the progress of asynchronous operations (like firmware pushes or syslog uploads) by searching job groups.
Parameters:
job_type – Type of job to search (default: command)
subtype (optional) – Further refine the job type
search_string – Filter by job name or description
limit / offset – Pagination controls
tenant_id (optional)
Example use: "Check the status of my firmware update job" or "List all recently run command jobs."
Here's a concise example prompt for each of the 23 Percepxion tools:
##  Authentication
login_with_env
"Log in to Percepxion using my environment credentials."
##  Device Inventory & Discovery
get_device_list
"List all devices in my inventory, sorted by device name."
get_device_details
"Get full details for device ID abc-123."
get_devices_by_organization
"Show all devices assigned to tenant org-456."
##  Device Configuration
update_device_config
"Update the DNS server setting on device abc-123 to 8.8.8.8 and apply it immediately."
clone_device_config
"Clone the VLAN and interface config records from device src-001 to device tgt-002."
🖥️ CLI Commands
send_direct_cli_command
"Run show version on device abc-123 and return the output."
send_cli_command
"Send the command show interfaces status to device abc-123."
🔄 Firmware Management
get_device_firmware_status
"What firmware version is device abc-123 currently running?"
firmware_compliance_report
"Generate a firmware compliance report — I want to know which devices are NOT on version 7.2.1."
update_firmware_by_smart_group
"Push the firmware file at /uploads/fw-7.2.1.bin, version 7.2.1, to Smart Groups sg-001 and sg-002."
🗂️ Smart Groups
automate_smart_group
"Create a Smart Group called 'Building A Switches' using the query location:building-a AND type:switch."
— or for an explicit list:
"Create a temporary Smart Group called 'Batch Update Set' containing device IDs d-001, d-002, and d-003."
📥 Device Lifecycle
import_and_assign_devices
"Onboard these three new devices into tenant org-456:"
[
  { "device_id": "d-001", "device_name": "switch-01", "serial_num": "SN123" },
  { "device_id": "d-002", "device_name": "switch-02", "serial_num": "SN124" }
]
unassign_devices
"Unassign devices d-001 and d-002 from their current tenant so I can reassign them."
remove_device_from_platform
"Permanently remove device abc-123 from the Percepxion platform — it's been decommissioned."
##  Logging & Monitoring
get_device_syslogs
"Show me the 20 most recent syslog entries already uploaded for device abc-123."
request_device_syslog_upload
"Upload error-level syslogs from devices d-001 and d-002 for the date range 2026-02-01T00:00:00Z to 2026-03-01T00:00:00Z."
query_device_access_log
"Show the last 50 access log entries for device abc-123, starting from offset 0."
download_device_access_log
"Download the full access log for device abc-123 at info level."
get_security_telemetry
"Pull the security telemetry stats for device abc-123 — I want to check for anything unusual."
🔍 Audit & Job Tracking
investigate_audit_logs
"Search audit logs for any actions taken by user jane.smith between 2026-02-01 and 2026-03-01."
investigate_user_audit_logs
"List all users and show the last action each one performed — filter for anyone matching admin."
search_job_groups
"Check the status of all firmware update jobs run in the last session."
These prompts can be spoken naturally