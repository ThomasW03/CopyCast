-- Initial schema: sources, media items, profiles and per-profile playback progress.

CREATE TABLE sources (
    id          INTEGER PRIMARY KEY,
    kind        TEXT    NOT NULL CHECK (kind IN ('local', 'webdav')),
    name        TEXT    NOT NULL,
    uri         TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE media_items (
    id           INTEGER PRIMARY KEY,
    source_id    INTEGER NOT NULL REFERENCES sources (id) ON DELETE CASCADE,
    kind         TEXT    NOT NULL CHECK (kind IN ('movie', 'episode', 'track', 'podcast_episode')),
    title        TEXT    NOT NULL,
    year         INTEGER,
    duration_ms  INTEGER NOT NULL DEFAULT 0,
    path         TEXT    NOT NULL,
    poster_path  TEXT,
    added_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (source_id, path)
);

CREATE INDEX media_items_kind ON media_items (kind);

CREATE TABLE profiles (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE,
    is_child    INTEGER NOT NULL DEFAULT 0 CHECK (is_child IN (0, 1)),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE playback_progress (
    profile_id   INTEGER NOT NULL REFERENCES profiles (id) ON DELETE CASCADE,
    media_id     INTEGER NOT NULL REFERENCES media_items (id) ON DELETE CASCADE,
    position_ms  INTEGER NOT NULL DEFAULT 0,
    watched      INTEGER NOT NULL DEFAULT 0 CHECK (watched IN (0, 1)),
    updated_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (profile_id, media_id)
);
