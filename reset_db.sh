#!/bin/bash
set -e

echo ">>> Activating virtual environment..."
source /home/user/prodvor-backend/.venv/bin/activate

echo ">>> Downgrading database to base..."
alembic -c migrations/alembic.ini downgrade base

echo ">>> Upgrading database to head..."
alembic -c migrations/alembic.ini upgrade head

echo ">>> Database reset complete."
