//! `GET /library/items` and `GET /library/items/{item_id}`. Stub: serves the fixtures.

use axum::Router;
use axum::extract::Path;
use axum::response::IntoResponse;
use axum::routing::get;

use crate::fixtures;
use crate::state::AppState;

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/library/items", get(list_items))
        .route("/library/items/{item_id}", get(get_item))
}

async fn list_items() -> impl IntoResponse {
    fixtures::json_response(fixtures::LIBRARY_ITEMS)
}

async fn get_item(Path(_item_id): Path<i64>) -> impl IntoResponse {
    fixtures::json_response(fixtures::LIBRARY_ITEM)
}
