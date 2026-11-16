//! Runs the control API until a shutdown is requested.

use std::net::SocketAddr;

use anyhow::{Context, Result};
use axum::Router;
use tokio::net::TcpListener;

use crate::shutdown;

pub async fn serve(address: SocketAddr, app: Router) -> Result<()> {
    let listener = TcpListener::bind(address)
        .await
        .with_context(|| format!("cannot listen on {address}"))?;
    tracing::info!(%address, "control API listening");
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown::wait_for_signal())
        .await
        .context("the control API stopped unexpectedly")
}
