-- Enable the pgcrypto extension in PostgreSQL.
--
-- pgcrypto provides the pgp_sym_encrypt() and pgp_sym_decrypt() functions
-- that the application uses to encrypt clinical entry content at rest.
-- This script runs automatically when the database container first starts
-- (it is mounted at /docker-entrypoint-initdb.d/ in docker-compose.yml).
-- The IF NOT EXISTS guard makes it safe to run multiple times.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
