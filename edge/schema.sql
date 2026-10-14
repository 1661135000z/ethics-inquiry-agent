CREATE TABLE IF NOT EXISTS sessions (
 token TEXT PRIMARY KEY, payload TEXT NOT NULL, expires INTEGER NOT NULL,
 busy TEXT NOT NULL DEFAULT '', busy_until INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires);
CREATE TABLE IF NOT EXISTS requests (
 token TEXT NOT NULL, request_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
 created INTEGER NOT NULL, result TEXT,
 PRIMARY KEY(token,request_id)
);
CREATE INDEX IF NOT EXISTS requests_created ON requests(created);
