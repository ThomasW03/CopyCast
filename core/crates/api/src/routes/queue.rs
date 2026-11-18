//! `GET /queue`: items waiting to be played. Stub: serves the fixture.

use axum::Router;
use axum::response::IntoResponse;
use axum::routing::get;

use crate::fixtures;
use crate::state::AppState;

pub fn routes() -> Router<AppState> {
    Router::new().route("/queue", get(get_queue))
}

async fn get_queue() -> impl IntoResponse {
    fixtures::json_response(fixtures::QUEUE)
}
