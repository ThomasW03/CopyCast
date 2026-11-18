//! Wires the daemon together: database, control API and network announcement.

use anyhow::Result;
use copycast_api::{AppState, EventBus, router};
use mdns_sd::ServiceDaemon;

use crate::config::Config;
use crate::{database, discovery, server};

pub async fn run(config: Config) -> Result<()> {
    let database = database::open(&config.database_path()).await?;
    let state = AppState::new(database, EventBus::new());
    let announcement = start_announcement(&config);

    let result = server::serve(config.address(), router(state)).await;

    stop_announcement(announcement);
    result
}

/// Announcing is optional: without it the daemon still works, phones just cannot find it.
fn start_announcement(config: &Config) -> Option<ServiceDaemon> {
    if !config.is_exposed() {
        tracing::info!("listening on this machine only, not announcing on the network");
        return None;
    }
    match discovery::advertise(config.port) {
        Ok(announcement) => Some(announcement),
        Err(error) => {
            tracing::warn!(%error, "network announcement disabled");
            None
        }
    }
}

fn stop_announcement(announcement: Option<ServiceDaemon>) {
    if let Some(announcement) = announcement
        && let Err(error) = announcement.shutdown()
    {
        tracing::warn!(%error, "cannot stop the network announcement cleanly");
    }
}
