-- FindIt schema (idempotent – safe to run on every start)
CREATE TABLE IF NOT EXISTS findit_users (
    id            SERIAL PRIMARY KEY,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findit_sessions (
    token         TEXT PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES findit_users(id) ON DELETE CASCADE,
    expires_at    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findit_items (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER REFERENCES findit_users(id) ON DELETE SET NULL,
    type          TEXT NOT NULL,
    reporter      TEXT NOT NULL,
    title         TEXT NOT NULL,
    category      TEXT NOT NULL,
    description   TEXT NOT NULL,
    location      TEXT NOT NULL,
    item_date     TIMESTAMPTZ NOT NULL,
    photo_url     TEXT,
    private_detail TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'OPEN',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findit_matches (
    id            SERIAL PRIMARY KEY,
    lost_item_id  INTEGER NOT NULL REFERENCES findit_items(id) ON DELETE CASCADE,
    found_item_id INTEGER NOT NULL REFERENCES findit_items(id) ON DELETE CASCADE,
    score         REAL NOT NULL,
    verified      BOOLEAN NOT NULL DEFAULT FALSE,
    lost_confirmed  BOOLEAN NOT NULL DEFAULT FALSE,
    found_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    attempts_count  INTEGER NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT findit_matches_lost_found_unique UNIQUE (lost_item_id, found_item_id)
);

CREATE TABLE IF NOT EXISTS findit_messages (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER NOT NULL REFERENCES findit_matches(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    text        TEXT NOT NULL,
    sent_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
