#!/bin/sh

# Run the initial sync
python -m src.main

# Start cron service
echo "Starting cron service..."
exec cron -f