# Start from the same base image
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set timezone to avoid issues with cron scheduling
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install cron
RUN apt-get update && apt-get install -y cron

# Set working directory
WORKDIR /app

# Copy application code and install dependencies
COPY src/ /app/src/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy cron file and set permissions
COPY scraper-cron /etc/cron.d/scraper-cron
RUN chmod 0644 /etc/cron.d/scraper-cron && \
    touch /var/log/cron.log

# Copy entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["entrypoint.sh"]