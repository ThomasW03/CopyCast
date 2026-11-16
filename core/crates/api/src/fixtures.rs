//! Example payloads from `contracts/fixtures/`, served by the stub routes until the real
//! implementation replaces them.

use axum::http::header;
use axum::response::IntoResponse;

pub const LIBRARY_ITEMS: &str = include_str!("../../../../contracts/fixtures/library-items.json");
pub const LIBRARY_ITEM: &str = include_str!("../../../../contracts/fixtures/library-item.json");
pub const PLAYBACK_STATE: &str = include_str!("../../../../contracts/fixtures/playback-state.json");
pub const QUEUE: &str = include_str!("../../../../contracts/fixtures/queue.json");
pub const PAIRING_REQUEST: &str =
    include_str!("../../../../contracts/fixtures/pairing-request.json");
pub const PAIRING_TOKEN: &str = include_str!("../../../../contracts/fixtures/pairing-token.json");

/// Wraps an embedded JSON document in a response with the right content type.
pub fn json_response(body: &'static str) -> impl IntoResponse {
    ([(header::CONTENT_TYPE, "application/json")], body)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_fixture_is_valid_json() {
        let fixtures = [
            LIBRARY_ITEMS,
            LIBRARY_ITEM,
            PLAYBACK_STATE,
            QUEUE,
            PAIRING_REQUEST,
            PAIRING_TOKEN,
        ];

        for fixture in fixtures {
            serde_json::from_str::<serde_json::Value>(fixture).unwrap();
        }
    }
}
