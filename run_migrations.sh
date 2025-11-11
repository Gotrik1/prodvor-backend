#!/bin/bash
set -e

# Check for migration message
if [ -z "$1" ]; then
  echo "Error: Migration message is required."
  echo "Usage: ./run_migrations.sh \"Your descriptive migration message\""
  exit 1
fi

echo ">>> Activating virtual environment..."
source /home/user/prodvor-backend/.venv/bin/activate

echo ">>> Generating new revision: $1"
alembic -c migrations/alembic.ini revision --autogenerate -m "$1"

echo ">>> Applying migration to database..."
alembic -c migrations/alembic.ini upgrade head

echo ">>> Done."