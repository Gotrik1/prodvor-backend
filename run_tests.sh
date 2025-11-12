#!/bin/bash

# A more robust way to kill the server process.
echo "Ensuring port 8080 is free by stopping any running uvicorn server..."
pkill -f uvicorn || true
sleep 2

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Set and export the database URL
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres"

# Completely wipe the database
echo "Wiping the database completely..."
python clear_db.py

# Run database migrations from scratch
echo "Running database migrations..."
alembic -c migrations/alembic.ini upgrade head

# Start the server in the background
echo "Starting server on port 8080..."
uvicorn app.main:app --host 0.0.0.0 --port 8080 &
SERVER_PID=$!

# Wait for the server to start up.
echo "Waiting 10 seconds for server to start..."
sleep 10

# Check for a specific test target passed as an argument
TEST_TARGET=$1

# Deactivate exit on error to manually handle test exit code and use pipefail
set +e -o pipefail

# Run the tests and format output
if [ -n "$TEST_TARGET" ]; then
  echo "Running tests for module: $TEST_TARGET"
  (cd tests && API_BASE_URL=http://localhost:8080 npm test -- "$TEST_TARGET.test.ts") 2>&1 | sed -E 's/^(PASS.*)/✅ /; s/^(FAIL.*)/❌ /'
  TEST_EXIT_CODE=${PIPESTATUS[0]}
else
  echo "Running all tests..."
  (cd tests && API_BASE_URL=http://localhost:8080 npm test) 2>&1 | sed -E 's/^(PASS.*)/✅ /; s/^(FAIL.*)/❌ /'
  TEST_EXIT_CODE=${PIPESTATUS[0]}
fi

# Re-enable exit on error
set -e

# Kill the specific server process we started
echo "Shutting down server..."
pkill -f uvicorn || true

echo "Tests finished with exit code: $TEST_EXIT_CODE"
exit $TEST_EXIT_CODE
