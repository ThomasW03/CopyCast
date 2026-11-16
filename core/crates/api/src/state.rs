//! State shared by every route handler.

use std::time::Instant;

use sqlx::SqlitePool;

use crate::EventBus;

#[derive(Debug, Clone)]
pub struct AppState {
    pub started_at: Instant,
    pub events: EventBus,
    pub db: SqlitePool,
}

impl AppState {
    pub fn new(db: SqlitePool, events: EventBus) -> Self {
        Self {
            started_at: Instant::now(),
            events,
            db,
        }
    }
}
