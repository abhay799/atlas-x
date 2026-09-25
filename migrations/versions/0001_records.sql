CREATE TABLE IF NOT EXISTS atlas_records (
 id INTEGER PRIMARY KEY,
 kind VARCHAR(64) NOT NULL,
 key VARCHAR(128) NOT NULL,
 payload TEXT NOT NULL,
 created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_atlas_records_kind_key ON atlas_records(kind,key);
