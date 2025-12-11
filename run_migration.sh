#!/bin/bash

# Run migration to change earthquake_id from INTEGER to VARCHAR
# This script connects to the PostgreSQL database and runs the migration

echo "Running migration: Change earthquake_id to VARCHAR..."

# Option 1: If using docker-compose
docker-compose exec db psql -U postgres -d smrm_db -f /var/lib/postgresql/data/migration_earthquake_id_to_string.sql

# Option 2: If connecting directly to local database
# psql -h localhost -p 7432 -U postgres -d smrm_db -f migration_earthquake_id_to_string.sql

echo "Migration completed!"
