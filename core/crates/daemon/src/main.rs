//! Entry point of the CopyCast daemon.

mod app;
mod config;
mod database;
mod discovery;
mod logging;
mod server;
mod shutdown;

use clap::Parser;

use crate::config::Config;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    logging::init();
    app::run(Config::parse()).await
}
