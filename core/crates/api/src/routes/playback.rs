//! `GET /playback` and `POST /playback/commands`. Stub: serves the fixture and accepts commands.

use axum::Router;
use axum::extract::Json;
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::routing::{get, post};

use crate::command::PlaybackCommand;
use crate::fixtures;
use crate::state::AppState;

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/playback", get(get_state))
        .route("/playback/commands", post(send_command))
}

async fn get_state() -> impl IntoResponse {
    fixtures::json_response(fixtures::PLAYBACK_STATE)
}

async fn send_command(Json(command): Json<PlaybackCommand>) -> StatusCode {
    tracing::info!(?command, "playback command accepted (stub)");
    StatusCode::ACCEPTED
}
