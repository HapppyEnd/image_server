#!/bin/bash

BACKUP_DIR="${BACKUP_DIR:-./backups}"
PG_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-image_db}"
NOW=$(date '+%Y-%m-%d_%H%M%S')
FILE_NAME="backup_$NOW.sql"
BACKUP_PATH="$BACKUP_DIR/$FILE_NAME"

CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' db 2>/dev/null)

case "$CONTAINER_STATUS" in
    running)
        ;;
    "")
        echo "Error: Container 'db' does not exist" >&2
        exit 1
        ;;
    *)
        echo "Error: Container 'db' is $CONTAINER_STATUS (must be running)" >&2
        exit 1
        ;;
esac

mkdir -p "$BACKUP_DIR"

echo "Creating PostgreSQL backup of $DB_NAME..."
if docker exec -t db pg_dump -U "$PG_USER" "$DB_NAME" > "$BACKUP_PATH"; then
    echo "Backup successfully created: $BACKUP_PATH"
    exit 0
else
    echo "Backup failed!" >&2
    if [ -f "$BACKUP_PATH" ]; then
        rm -f "$BACKUP_PATH"
        echo "Removed incomplete backup file: $BACKUP_PATH" >&2
    fi
    exit 1
fi