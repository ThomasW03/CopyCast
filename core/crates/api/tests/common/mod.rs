//! Helpers shared by the integration tests.
//!
//! Each test file compiles this module on its own, so helpers it does not use are expected.
#![allow(dead_code)]

use std::net::SocketAddr;

use axum::body::Body;
use axum::http::{Method, Request, StatusCode};
use copycast_api::{AppState, EventBus, router};
use http_body_util::BodyExt;
use serde_json::Value;
use sqlx::sqlite::SqlitePoolOptions;
use tokio::net::TcpListener;
use tower::ServiceExt;

pub async fn test_state() -> AppState {
    let db = SqlitePoolOptions::new()
        .connect("sqlite::memory:")
        .await
        .expect("in-memory database opens");
    AppState::new(db, EventBus::new())
}

pub async fn get_json(state: AppState, uri: &str) -> (StatusCode, Value) {
    let request = Request::get(uri).body(Body::empty()).unwrap();
    call(state, request).await
}

pub async fn post_json(state: AppState, uri: &str, body: Value) -> (StatusCode, Value) {
    let request = Request::builder()
        .method(Method::POST)
        .uri(uri)
        .header("content-type", "application/json")
        .body(Body::from(body.to_string()))
        .unwrap();
    call(state, request).await
}

/// Starts the API on a free local port and returns its address.
pub async fn spawn_server(state: AppState) -> SocketAddr {
    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    tokio::spawn(async move {
        axum::serve(listener, router(state)).await.unwrap();
    });
    address
}

async fn call(state: AppState, request: Request<Body>) -> (StatusCode, Value) {
    let response = router(state).oneshot(request).await.unwrap();
    let status = response.status();
    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    (status, parse_body(&bytes))
}

/// An empty body (for example `202 Accepted`) is reported as JSON `null`.
fn parse_body(bytes: &[u8]) -> Value {
    if bytes.is_empty() {
        return Value::Null;
    }
    serde_json::from_slice(bytes).unwrap_or(Value::Null)
}
