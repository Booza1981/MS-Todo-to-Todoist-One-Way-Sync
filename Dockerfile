# Start from the same base image
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set timezone to avoid issues with cron scheduling
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy application code
WORKDIR /app
COPY src/ /app/src/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add the crontab file to the cron directory
COPY scraper-cron /etc/cron.d/scraper-cron

# Give execution rights on the cron job and create the log file
RUN chmod 0644 /etc/cron.d/scraper-cron && \
    touch /var/log/cron.log

# Run the command on container startup
# Starts cron and tails the log file to keep the container running and show logs.
CMD ["cron", "-f"]