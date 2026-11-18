mod common;

use axum::http::StatusCode;
use common::{get_json, test_state};

#[tokio::test]
async fn health_reports_version_and_uptime() {
    let (status, body) = get_json(test_state().await, "/api/v1/health").await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["version"], env!("CARGO_PKG_VERSION"));
    assert!(body["uptime_seconds"].is_u64());
}

#[tokio::test]
async fn unknown_routes_return_not_found() {
    let (status, _) = get_json(test_state().await, "/api/v1/nothing").await;

    assert_eq!(status, StatusCode::NOT_FOUND);
}
