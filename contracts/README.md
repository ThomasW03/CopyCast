# Contracts

Shared agreements between the daemon (`core/`), the living-room app (`app/`) and the remote app (`mobile/`). Code against these files, not against each other's code.

| File | Describes |
| --- | --- |
| `openapi.yaml` | HTTP control API (`/api/v1`) |
| `events.schema.json` | Messages pushed over the WebSocket |
| `extension-manifest.schema.json` | The `manifest.json` of an extension |
| `fixtures/` | Example payloads, served by the daemon's stub routes and reused in tests |

## Rules

- A route or event is added here first, then implemented.
- Changes to this folder are reviewed by every team member.
- Every fixture must validate against its schema.
