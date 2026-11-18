//! `GET /health`: liveness probe and daemon version.

use axum::extract::State;
use axum::routing::get;
use axum::{Json, Router};
use serde::Serialize;

use crate::VERSION;
use crate::state::AppState;

pub fn routes() -> Router<AppState> {
    Router::new().route("/health", get(get_health))
}

#[derive(Debug, Serialize)]
struct Health {
    version: &'static str,
    uptime_seconds: u64,
}

async fn get_health(State(state): State<AppState>) -> Json<Health> {
    Json(Health {
        version: VERSION,
        uptime_seconds: state.started_at.elapsed().as_secs(),
    })
}
