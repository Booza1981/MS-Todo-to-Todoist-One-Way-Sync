#!/bin/sh

echo "Entrypoint script started."

# Check for auth.json
if [ ! -f "/app/auth.json" ]; then
  echo "Error: /app/auth.json not found or is not a regular file."
  echo "Please ensure you have generated it using 'python3 src/main.py --setup' and it is mounted correctly."
  exit 1
fi
echo "Found /app/auth.json."

# Check for environment variable
if [ -z "$TODOIST_API_TOKEN" ]; then
  echo "Error: TODOIST_API_TOKEN environment variable is not set."
  echo "Please ensure it is defined in your .env file."
  exit 1
fi
echo "Found TODOIST_API_TOKEN."

# Run the initial sync
echo "Running initial sync..."
python -m src.main

# Start cron service
echo "Starting cron service..."
exec cron -f