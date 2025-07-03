# Microsoft To-Do to Todoist Scraper

## Overview

This project scrapes tasks from your Microsoft To-Do account and syncs them to a specified Todoist project. It helps you consolidate your tasks from different sources into a single, unified view in Todoist.

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

*   Python 3
*   Docker (recommended for easy deployment)

## Setup & Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/todo-scraper.git
    cd todo-scraper
    ```
2.  **Create the `.env` file:**
    *   Copy the `.env.example` file to a new file named `.env`.
    *   Add your Todoist API token to the `TODOIST_API_TOKEN` variable.
3.  **One-Time Authentication:**
    *   Run the following command to generate the `auth.json` file for Microsoft To-Do authentication:
        ```bash
        python3 scraper.py --setup
        ```

## Usage

### Manual Execution

To run the scraper manually, use the following command:

```bash
python -m src.main
```

### Recommended: Docker

For a more consistent and portable environment, you can use the provided Docker setup:

```bash
docker build -t todo-scraper .
docker run --rm -v $(pwd)/.env:/app/.env -v $(pwd)/auth.json:/app/auth.json todo-scraper
```

## Deployment (Automation)

To automate the script, you can set up a cron job to run the Docker command at regular intervals. For example, to run the scraper every hour, add the following to your crontab:

```bash
0 * * * * cd /path/to/your/project && docker run --rm -v $(pwd)/.env:/app/.env -v $(pwd)/auth.json:/app/auth.json todo-scraper