//! Log output setup.

use tracing_subscriber::EnvFilter;

const DEFAULT_FILTER: &str = "info";

/// Logs to stderr. The level can be changed with the `RUST_LOG` environment variable.
pub fn init() {
    let filter =
        EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(DEFAULT_FILTER));
    tracing_subscriber::fmt().with_env_filter(filter).init();
}
