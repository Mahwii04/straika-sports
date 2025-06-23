#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Initialize database if migrations folder doesn't exist
if [ ! -d "migrations" ]; then
    flask db init
    # Create initial migration with all current models
    flask db migrate -m "Initial migration"
fi

# Always apply migrations
flask db upgrade