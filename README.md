# Microsoft To-Do to Todoist Scraper

## Overview

This project scrapes tasks from your Microsoft To-Do account and syncs them to a specified Todoist project. It helps you consolidate your tasks from different sources into a single, unified view in Todoist.

The application is designed to run inside a Docker container and is automatically scheduled to run every 4 hours using a cron job.

## Features

*   **Comprehensive Scraping:** Scrapes tasks from the "Tasks", "Flagged email", and "Assigned to me" sections of your Microsoft To-Do account.
*   **Configurable Syncing:** Syncs all scraped tasks to a Todoist project that you can configure.
*   **Smart Tag Parsing:**
    *   Parses `[Due: DD/MM/YYYY]` tags in your task names to automatically set due dates in Todoist.
    *   Recognizes `[Important]` tags to set the priority of your tasks.
*   **Automatic Labeling:** Applies "Flagged:" and "Assigned:" prefixes as labels in Todoist to help you categorize and filter tasks.
*   **Duplicate Prevention:** Prevents the creation of duplicate tasks, ensuring your Todoist project remains clean and organized.
*   **Task Completion Sync:** Closes tasks in Todoist that have been completed or deleted in Microsoft To-Do, keeping both platforms in sync.
*   **Orchestrated Execution:** A single `main.py` script orchestrates the entire scraping and syncing process for easy execution.

## Prerequisites

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   A local machine with a graphical interface for the one-time setup.

## Setup and Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/todo-scraper.git
cd todo-scraper
```

### 2. Headless Server Authentication

To run this scraper on a headless server, you must first generate the `auth.json` session file on a local machine that has a web browser.

**Step 1: Generate `auth.json` Locally**

On your local machine (not the server), run the interactive setup command. This will open a browser window where you can log in to your Microsoft account.

```bash
# Make sure Docker is running on your local machine
python3 src/main.py --setup
```

Follow the on-screen instructions. After you log in successfully, press `Enter` in the terminal. An `auth.json` file will be created in your project directory.

> **Security Note:** The `auth.json` file contains sensitive session information. It is already listed in `.gitignore` and should **never** be committed to your repository.

**Step 2: Securely Transfer `auth.json` to the Server**

Copy the generated `auth.json` file to the project directory on your headless server. You can use `scp` or any other secure file transfer method.

Example using `scp`:

```bash
scp /path/to/your/local/auth.json user@your-server-ip:/path/to/your/project/
```

### 3. Configure Environment Variables

On your server, create a `.env` file from the example provided:

```bash
cp .env.example .env
```

Edit the `.env` file and add your Todoist API token:

```
TODOIST_API_TOKEN=your_todoist_api_token_here
TODOIST_PROJECT_NAME=Microsoft To-Do
INPUT_FILE=tasks.txt
```

## Usage

### Running the Scraper

With `auth.json` and `.env` in place, you can start the scheduled scraper with a single command. The `docker-compose.yml` is pre-configured to mount these files into the container.

```bash
docker-compose up -d
```

This will build the Docker image and start the container in the background. The scraper will now run automatically every 4 hours.

### Checking Logs

To see the output from the scraper, you can view the container's logs:

```bash
docker-compose logs -f
```

> **Note:** An initial sync will run immediately when the container starts. You will see the log output right away. Subsequent syncs will occur automatically every 4 hours.

### Stopping the Scraper

To stop the container and remove the network, run:

```bash
docker-compose down
```