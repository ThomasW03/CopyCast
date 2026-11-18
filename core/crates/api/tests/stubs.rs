//! The stub routes serve the fixtures of `contracts/fixtures/` until the real logic exists.

mod common;

use axum::http::StatusCode;
use common::{get_json, post_json, test_state};
use copycast_api::Event;
use serde_json::json;

#[tokio::test]
async fn library_items_are_served_from_the_fixture() {
    let (status, body) = get_json(test_state().await, "/api/v1/library/items").await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body.as_array().unwrap().len(), 3);
    assert_eq!(body[0]["title"], "Big Buck Bunny");
}

#[tokio::test]
async fn a_single_library_item_is_served() {
    let (status, body) = get_json(test_state().await, "/api/v1/library/items/1").await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["id"], 1);
}

#[tokio::test]
async fn playback_state_is_served() {
    let (status, body) = get_json(test_state().await, "/api/v1/playback").await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["status"], "playing");
}

#[tokio::test]
async fn queue_is_served() {
    let (status, body) = get_json(test_state().await, "/api/v1/queue").await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body.as_array().unwrap().len(), 2);
}

#[tokio::test]
async fn a_valid_playback_command_is_accepted() {
    let command = json!({ "action": "seek", "position_ms": 5000 });

    let (status, _) = post_json(test_state().await, "/api/v1/playback/commands", command).await;

    assert_eq!(status, StatusCode::ACCEPTED);
}

#[tokio::test]
async fn an_unknown_playback_command_is_rejected() {
    let command = json!({ "action": "explode" });

    let (status, _) = post_json(test_state().await, "/api/v1/playback/commands", command).await;

    assert_eq!(status, StatusCode::UNPROCESSABLE_ENTITY);
}

#[tokio::test]
async fn a_pairing_request_announces_the_code_to_the_screen() {
    let state = test_state().await;
    let mut events = state.events.subscribe();

    let (status, body) = post_json(
        state,
        "/api/v1/pairing/requests",
        json!({ "device_name": "Pixel 8" }),
    )
    .await;

    assert_eq!(status, StatusCode::CREATED);
    assert_eq!(body["request_id"], "req_demo");
    let Event::PairingRequested { device_name, .. } = events.recv().await.unwrap() else {
        panic!("expected a pairing.requested event");
    };
    assert_eq!(device_name, "Pixel 8");
}

#[tokio::test]
async fn confirming_a_pairing_request_returns_a_token() {
    let (status, body) = post_json(
        test_state().await,
        "/api/v1/pairing/requests/req_demo/confirm",
        json!({ "code": "482913" }),
    )
    .await;

    assert_eq!(status, StatusCode::OK);
    assert!(body["token"].is_string());
}
