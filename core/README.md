# Core

The CopyCast daemon, written in Rust. It owns the library database and serves the control API that the living-room app and the remote app connect to.

## Layout

| Path | Responsibility |
| --- | --- |
| `crates/api` | HTTP and WebSocket control API: routes, events, shared state |
| `crates/daemon` | The executable: configuration, database, network announcement, server, shutdown |
| `migrations/` | SQLite schema, applied automatically at startup |

The API contract is in [`../contracts`](../contracts). Routes and events are added there first.

## Run

```bash
cd core
cargo run -p copycast-daemon
```

The daemon listens on `127.0.0.1:7878` and only accepts connections from this machine. To let a phone on the local network connect, listen on all interfaces:

```bash
cargo run -p copycast-daemon -- --host 0.0.0.0
```

| Option | Environment variable | Default |
| --- | --- | --- |
| `--host` | `COPYCAST_HOST` | `127.0.0.1` |
| `--port` | `COPYCAST_PORT` | `7878` |
| `--data-dir` | `COPYCAST_DATA_DIR` | the user data directory of the operating system |

When the host is not a loopback address, the daemon announces itself over mDNS as `_copycast._tcp`.

Try it:

```bash
curl http://127.0.0.1:7878/api/v1/health
```

In PowerShell, `curl` is an alias of `Invoke-WebRequest` and does not accept the options of the real curl. Use `curl.exe`, or `Invoke-RestMethod`:

```powershell
curl.exe http://127.0.0.1:7878/api/v1/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:7878/api/v1/playback/commands `
  -ContentType "application/json" -Body '{"action":"pause"}'
```

More examples (pairing, events, discovery) are in [the control API guide](../docs/technical/control-api.md).

The routes under `library`, `playback`, `queue` and `pairing` are stubs that serve the examples of `contracts/fixtures/`. The control API does not authenticate devices yet: do not expose it on an untrusted network.

Known limitations of the skeleton, to fix before the API is exposed (`--host 0.0.0.0`) outside development:

- The WebSocket accepts any client, with no bearer token and no check of the `Origin` header.
- The pairing code is published on the shared event bus, so every connected WebSocket client receives it. It must only reach the living-room screen, through an authenticated or local-only channel.

## Test and check

```bash
cargo test
cargo fmt --all --check
cargo clippy --all-targets -- -D warnings
```

Run a single test with `cargo test <name>`, for example `cargo test health`.

## Add a route

1. Describe it in `contracts/openapi.yaml`, and add a fixture if it returns data.
2. Create `crates/api/src/routes/<resource>.rs` with a `routes()` function, and declare it in `routes/mod.rs` and `router.rs`.
3. Add a test in `crates/api/tests/`.

## Conventions

- One responsibility per file, at most 300 lines per file.
- Small functions that do one thing.
- Code, comments and documentation are written in English.
