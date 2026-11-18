//! SQLite connection and schema migrations.

use std::path::Path;

use anyhow::{Context, Result};
use sqlx::SqlitePool;
use sqlx::sqlite::{SqliteConnectOptions, SqlitePoolOptions};

/// Opens the database (creating it if needed) and brings its schema up to date.
pub async fn open(path: &Path) -> Result<SqlitePool> {
    create_parent_directory(path)?;
    let pool = connect(path).await?;
    migrate(&pool).await?;
    Ok(pool)
}

fn create_parent_directory(path: &Path) -> Result<()> {
    let Some(directory) = path.parent() else {
        return Ok(());
    };
    std::fs::create_dir_all(directory)
        .with_context(|| format!("cannot create data directory {}", directory.display()))
}

async fn connect(path: &Path) -> Result<SqlitePool> {
    let options = SqliteConnectOptions::new()
        .filename(path)
        .create_if_missing(true)
        .foreign_keys(true);
    SqlitePoolOptions::new()
        .connect_with(options)
        .await
        .with_context(|| format!("cannot open database {}", path.display()))
}

async fn migrate(pool: &SqlitePool) -> Result<()> {
    sqlx::migrate!("../../migrations")
        .run(pool)
        .await
        .context("database migration failed")
}

#[cfg(test)]
mod tests {
    use super::*;

    const COUNT_MEDIA_ITEMS: &str = "SELECT COUNT(*) FROM media_items";
    const COUNT_PROFILES: &str = "SELECT COUNT(*) FROM profiles";

    async fn count_rows(pool: &SqlitePool, query: &'static str) -> i64 {
        sqlx::query_scalar(query).fetch_one(pool).await.unwrap()
    }

    #[tokio::test]
    async fn opening_creates_the_schema() {
        let directory = tempfile::tempdir().unwrap();

        let pool = open(&directory.path().join("nested").join("test.db"))
            .await
            .unwrap();

        assert_eq!(count_rows(&pool, COUNT_MEDIA_ITEMS).await, 0);
        assert_eq!(count_rows(&pool, COUNT_PROFILES).await, 0);
    }

    #[tokio::test]
    async fn opening_twice_keeps_existing_data() {
        let directory = tempfile::tempdir().unwrap();
        let path = directory.path().join("test.db");
        let first = open(&path).await.unwrap();
        sqlx::query("INSERT INTO profiles (name) VALUES ('Alex')")
            .execute(&first)
            .await
            .unwrap();
        first.close().await;

        let second = open(&path).await.unwrap();

        assert_eq!(count_rows(&second, COUNT_PROFILES).await, 1);
    }
}
