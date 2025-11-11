#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Start the server in the background
DATABASE_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres" uvicorn app.main:app --host 0.0.0.0 --port 8080 &

# Wait for the server to start
sleep 5

# Run the tests
cd tests && API_BASE_URL=http://localhost:8080 npm test

# Kill the server process
kill $!
