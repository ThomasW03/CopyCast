//! HTTP and WebSocket control API of the CopyCast daemon.
//!
//! The contract lives in `contracts/`: routes are added there first, then implemented here.

mod command;
mod event;
mod event_bus;
mod fixtures;
mod router;
mod routes;
mod state;

pub use command::PlaybackCommand;
pub use event::{Event, PlaybackStatus};
pub use event_bus::EventBus;
pub use router::router;
pub use state::AppState;

/// Version reported by the health route and the WebSocket greeting.
pub(crate) const VERSION: &str = env!("CARGO_PKG_VERSION");
