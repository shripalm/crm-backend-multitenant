#!/bin/bash

# Script to manage admin database migrations
export PYTHONPATH=$PYTHONPATH:$(pwd)

function create_database() {
    echo "Creating admin database if it doesn't exist..."
    python scripts/create_admin_db.py
}

function migrate() {
    echo "Running admin database migrations..."
    create_database
    alembic -c admin_alembic.ini upgrade head
}

function rollback() {
    echo "Rolling back admin database..."
    alembic -c admin_alembic.ini downgrade -1
}

function create_migration() {
    if [ -z "$1" ]; then
        echo "Please provide a migration message"
        exit 1
    fi
    echo "Creating new admin migration..."
    alembic -c admin_alembic.ini revision --autogenerate -m "$1"
}

case "$1" in
    "migrate")
        migrate
        ;;
    "rollback")
        rollback
        ;;
    "create")
        create_migration "$2"
        ;;
    *)
        echo "Usage: $0 {migrate|rollback|create <message>}"
        exit 1
        ;;
esac