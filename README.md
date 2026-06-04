# SmartThings Vehicle for Home Assistant

Home Assistant companion custom integration for SmartThings Hyundai/Kia/Genesis vehicle devices.

This project targets the case where Home Assistant's official SmartThings integration can authenticate with SmartThings but does not expose vehicle entities. The custom integration reuses the existing Home Assistant SmartThings OAuth token, reads vehicle status through the official SmartThings REST API, and can expose explicit opt-in controls.

## Initial scope

- Read-only vehicle sensors from SmartThings `/status`
- Manual refresh button
- Lock control support with safety-first UI defaults

High-risk controls such as unlock, engine start/stop, and HVAC are intentionally not enabled by default.
