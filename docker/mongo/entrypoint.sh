#!/bin/bash
set -e

# Wait for MongoDB to be ready
until mongosh --host 127.0.0.1 --eval 'print("Waiting for MongoDB...")' --quiet; do
    sleep 1
done

# Check if the database has been seeded already
if [ "$(mongosh --host 127.0.0.1 --eval 'db.getSiblingDB("'"$MONGO_DB_NAME"'").players.count()' --quiet)" == "0" ]; then
    echo "Database is empty. Seeding the database..."
    python3 /app/scripts/db_seed.py
else
    echo "Database already seeded. Skipping seeding."
fi

# Start MongoDB normally after the seed check
mongod --bind_ip_all