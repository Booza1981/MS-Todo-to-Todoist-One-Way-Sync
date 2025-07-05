#!/bin/sh

# Log that the container has started and run the initial sync
echo "Container has started. Performing initial sync..."
python /app/src/main.py
echo "Initial sync complete."
echo "------------------------------------------------"

# Log the cron schedule
echo "Cron job is scheduled to run every 4 hours."
echo "Current cron schedule:"
crontab -l
echo "------------------------------------------------"
echo "Waiting for next scheduled run... Logs will appear below."

# Start cron in the foreground
exec cron -f