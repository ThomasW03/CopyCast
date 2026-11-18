//! Completes when the operating system asks the daemon to stop.

use std::future::pending;

use tokio::signal;

pub async fn wait_for_signal() {
    tokio::select! {
        () = interrupt() => {}
        () = terminate() => {}
    }
    tracing::info!("shutdown requested");
}

/// Ctrl+C.
async fn interrupt() {
    if let Err(error) = signal::ctrl_c().await {
        tracing::error!(%error, "cannot listen for Ctrl+C");
        pending::<()>().await;
    }
}

/// SIGTERM, sent by service managers and containers.
#[cfg(unix)]
async fn terminate() {
    match signal::unix::signal(signal::unix::SignalKind::terminate()) {
        Ok(mut stream) => {
            stream.recv().await;
        }
        Err(error) => {
            tracing::error!(%error, "cannot listen for SIGTERM");
            pending::<()>().await;
        }
    }
}

#[cfg(not(unix))]
async fn terminate() {
    pending::<()>().await;
}
