//! Device pairing. Stub: shows a fixed code and accepts any confirmation.

use axum::Router;
use axum::extract::{Json, Path, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::routing::post;
use serde::Deserialize;

use crate::event::Event;
use crate::fixtures;
use crate::state::AppState;

/// Code announced to the living-room screen by the stub.
const STUB_CODE: &str = "482913";

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/pairing/requests", post(create_request))
        .route(
            "/pairing/requests/{request_id}/confirm",
            post(confirm_request),
        )
}

#[derive(Debug, Deserialize)]
struct PairingRequestInput {
    device_name: String,
}

async fn create_request(
    State(state): State<AppState>,
    Json(input): Json<PairingRequestInput>,
) -> impl IntoResponse {
    announce_code(&state, input.device_name);
    (
        StatusCode::CREATED,
        fixtures::json_response(fixtures::PAIRING_REQUEST),
    )
}

fn announce_code(state: &AppState, device_name: String) {
    state.events.publish(Event::PairingRequested {
        request_id: "req_demo".to_owned(),
        device_name,
        code: STUB_CODE.to_owned(),
    });
}

async fn confirm_request(Path(_request_id): Path<String>) -> impl IntoResponse {
    fixtures::json_response(fixtures::PAIRING_TOKEN)
}
