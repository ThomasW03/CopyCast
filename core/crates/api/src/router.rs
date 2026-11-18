//! Assembles every route under the versioned prefix.

use axum::Router;

use crate::routes::{health, library, pairing, playback, queue, ws};
use crate::state::AppState;

const API_PREFIX: &str = "/api/v1";

pub fn router(state: AppState) -> Router {
    Router::new().nest(API_PREFIX, api_v1()).with_state(state)
}

fn api_v1() -> Router<AppState> {
    Router::new()
        .merge(health::routes())
        .merge(ws::routes())
        .merge(pairing::routes())
        .merge(library::routes())
        .merge(playback::routes())
        .merge(queue::routes())
}
