# Control API

The daemon (`core/`) exposes an HTTP and WebSocket API on the local network. The living-room app and the remote app are its clients.

The API is defined by the files in [`contracts/`](../../contracts): this page explains how to use it and does not copy it. When this page and a contract disagree, the contract wins.

| Contract | Describes |
| --- | --- |
| [`openapi.yaml`](../../contracts/openapi.yaml) | Every HTTP route, request and response |
| [`events.schema.json`](../../contracts/events.schema.json) | Messages pushed over the WebSocket |
| [`fixtures/`](../../contracts/fixtures) | Example payloads |

## Status

The skeleton answers every route of the contract, but only `health` and the WebSocket are real. The other routes are **stubs**: they validate the request and return a fixed example. See [Current limitations](#current-limitations).

| Route | Behaviour today |
| --- | --- |
| `GET /api/v1/health` | Real: version and uptime |
| `GET /api/v1/ws` | Real: greeting, then every published event |
| `POST /api/v1/pairing/requests` | Stub: fixed request, fixed code `482913` |
| `POST /api/v1/pairing/requests/{requestId}/confirm` | Stub: always returns an example token |
| `GET /api/v1/library/items` | Stub: three example films |
| `GET /api/v1/library/items/{itemId}` | Stub: always the same item |
| `GET /api/v1/playback` | Stub: fixed state |
| `POST /api/v1/playback/commands` | Stub: validates the command, logs it, answers `202` |
| `GET /api/v1/queue` | Stub: two example films |

## Start the daemon

```bash
cd core
cargo run -p copycast-daemon
```

By default the daemon only accepts connections from the machine it runs on (`127.0.0.1:7878`). To let a phone on the local network connect, listen on all interfaces:

```bash
cargo run -p copycast-daemon -- --host 0.0.0.0
```

| Option | Environment variable | Default |
| --- | --- | --- |
| `--host` | `COPYCAST_HOST` | `127.0.0.1` |
| `--port` | `COPYCAST_PORT` | `7878` |
| `--data-dir` | `COPYCAST_DATA_DIR` | User data directory of the operating system |

## Examples

Every request below can be run in a Unix shell, or in PowerShell with `curl.exe`. In PowerShell, plain `curl` is an alias of `Invoke-WebRequest` and does not accept the same options, so write `curl.exe` or use `Invoke-RestMethod`.

### Health

```bash
curl http://127.0.0.1:7878/api/v1/health
```

```json
{ "version": "0.1.0", "uptime_seconds": 199 }
```

### List the library

```bash
curl http://127.0.0.1:7878/api/v1/library/items
```

### Send a playback command

Unix shell:

```bash
curl -i -X POST http://127.0.0.1:7878/api/v1/playback/commands \
  -H "content-type: application/json" \
  -d '{"action":"pause"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:7878/api/v1/playback/commands `
  -ContentType "application/json" -Body '{"action":"pause"}'
```

The answer is `202 Accepted` with an empty body. The command is selected by its `action` field:

| `action` | Other fields |
| --- | --- |
| `play` | `item_id` |
| `pause` | none |
| `resume` | none |
| `seek` | `position_ms` |
| `set_volume` | `level` (0 to 100) |

An unknown action, or a missing field, is refused with `422`.

## Pairing

A phone must be paired before it can control the media center. The flow of the contract is:

1. The phone asks to pair: `POST /pairing/requests` with its `device_name`. It receives a `request_id`.
2. The daemon announces the code to the living-room screen with a `pairing.requested` event.
3. The user reads the code on the screen and types it on the phone.
4. The phone confirms: `POST /pairing/requests/{requestId}/confirm` with the `code`. It receives a `token` to use as a bearer token.

Unix shell:

```bash
curl -X POST http://127.0.0.1:7878/api/v1/pairing/requests \
  -H "content-type: application/json" \
  -d '{"device_name":"Pixel 8"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:7878/api/v1/pairing/requests `
  -ContentType "application/json" -Body '{"device_name":"Pixel 8"}'
```

The stub answers `request_id: req_demo` and announces the code `482913`. Confirming with any code returns an example token, which nothing checks yet.

## Real-time events

`GET /api/v1/ws` upgrades to a WebSocket. Every message is a JSON object whose `type` field selects its shape.

| `type` | Sent when |
| --- | --- |
| `hello` | Once, right after the connection opens |
| `playback.state` | The playback state changes |
| `library.updated` | A scan added, changed or removed media |
| `pairing.requested` | A device asks to pair |

To watch the events from a terminal (works on every system with Node.js):

```bash
npx wscat -c ws://127.0.0.1:7878/api/v1/ws
```

You first receive the greeting:

```json
{ "type": "hello", "version": "0.1.0" }
```

Keep `wscat` open and send a pairing request from another terminal: a `pairing.requested` event with the code appears.

The daemon subscribes the client before sending the greeting, so no event published afterwards is missed. A client that reads too slowly may lose some events: the daemon logs a warning and keeps the connection open.

## Network discovery

When the daemon listens on a non-loopback address (`--host 0.0.0.0`), it announces itself with mDNS (Zeroconf):

| Field | Value |
| --- | --- |
| Service type | `_copycast._tcp` |
| Instance name | `CopyCast` |
| Port | The port of the API |
| TXT record | `version`, the daemon version |

A client finds the service, reads the address and port, then calls `/api/v1/health` to check it is a CopyCast daemon.

To check the announcement from another machine:

```bash
avahi-browse -r _copycast._tcp   # Linux
dns-sd -B _copycast._tcp         # macOS, or Windows with Bonjour
```

On Windows, the first start with `--host 0.0.0.0` makes the firewall ask to allow the daemon on private networks.

With the default host, the daemon does not announce anything. Real-network behaviour is not verified yet.

## Errors

The contract describes an error body `{ "code": "...", "message": "..." }`. The skeleton does not produce it yet:

| Case | Status today | Body today |
| --- | --- | --- |
| Unknown route | `404` | Empty |
| Invalid JSON, wrong content type or unknown command | `400`, `415` or `422` | Plain text from the framework |

## Current limitations

The skeleton is meant for development on one machine. Do not expose it on a network you do not trust.

- **No authentication.** Every route is open, including the playback commands. The contract requires a bearer token everywhere except `health` and the pairing routes.
- **Open WebSocket.** Any client can connect, and the pairing code is published on the shared event bus, so every connected client receives it.
- **Stubs.** The library, playback, queue and pairing routes return fixed examples.

Each limitation has an open issue in the GitHub project: pairing, authentication, WebSocket restrictions, error body, library, playback relay, contract checks, discovery check.
