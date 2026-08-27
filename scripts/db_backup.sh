#!/usr/bin/env bash
set -eo pipefail

BACKUP_DIR="${BACKUP_STORAGE_PATH:-/app/backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/portfolio_db_backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "========================================================================"
echo "💾 INITIATING DATABASE BACKUP: ${TIMESTAMP}"
echo "========================================================================"

if [ -z "${DATABASE_URL}" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not defined."
    exit 1
fi

# Execute compressed logical database dump
pg_dump "${DATABASE_URL}" --clean --if-exists --no-owner --no-privileges | gzip > "${BACKUP_FILE}"

echo "✔ Backup created successfully at: ${BACKUP_FILE}"
echo "✔ Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)"

# Retain backups for 30 days and purge older snapshots
find "${BACKUP_DIR}" -type f -name "portfolio_db_backup_*.sql.gz" -mtime +30 -exec rm {} \;
echo "✔ Retention policy enforced (Backups older than 30 days purged)."

echo "========================================================================"
echo "✅ DATABASE BACKUP COMPLETED"
echo "========================================================================"
