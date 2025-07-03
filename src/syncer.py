import os
import re
from datetime import datetime
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
TODOIST_PROJECT_NAME = os.getenv("TODOIST_PROJECT_NAME")
INPUT_FILE = os.getenv("INPUT_FILE")

def ensure_labels_exist(api, label_names):
    """
    Ensures that the given labels exist in Todoist, creating them if necessary.
    Returns a dictionary mapping label names to their IDs.
    """
    try:
        labels_paginator = api.get_labels()
        existing_labels = [label for page in labels_paginator for label in page]
        label_map = {label.name: label.id for label in existing_labels}
        
        for name in label_names:
            if name not in label_map:
                print(f"Label '{name}' not found. Creating it...")
                label = api.add_label(name=name)
                label_map[name] = label.id
                print(f"Label '{name}' created successfully.")
        
        return {name: label_map[name] for name in label_names}
    except Exception as error:
        print(f"Error managing labels: {error}")
        return {}

def main():
    """
    Main function to read tasks from a file and sync them to Todoist.
    """
    if not TODOIST_API_TOKEN:
        print("ERROR: TODOIST_API_TOKEN environment variable not set.")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Input file '{INPUT_FILE}' not found. Please run the scraper first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        tasks_to_sync = [line.strip() for line in f if line.strip()]

    if not tasks_to_sync:
        print("No tasks found in the input file. Nothing to sync.")
        return

    print(f"Found {len(tasks_to_sync)} tasks to sync.")

    api = TodoistAPI(TODOIST_API_TOKEN)

    # Ensure required labels exist
    required_labels = ["Flagged", "Assigned"]
    label_ids = ensure_labels_exist(api, required_labels)
    if len(label_ids) != len(required_labels):
        print("Could not create or verify required labels. Aborting sync.")
        return

    # Find project
    try:
        projects_paginator = api.get_projects()
        all_projects = [p for page in projects_paginator for p in page]
        project = next((p for p in all_projects if p.name == TODOIST_PROJECT_NAME), None)
    except Exception as error:
        print(f"Error finding project: {error}")
        return

    # Create project if it doesn't exist
    if project is None:
        print(f"Project '{TODOIST_PROJECT_NAME}' not found. Creating it now...")
        try:
            project = api.add_project(name=TODOIST_PROJECT_NAME)
            print(f"Project '{TODOIST_PROJECT_NAME}' created successfully.")
        except Exception as error:
            print(f"Error creating project: {error}")
            return

    if not project:
        print("Could not find or create project. Aborting sync.")
        return

    print(f"Found project '{project.name}' (ID: {project.id}). Syncing tasks...")

    # Get existing tasks
    try:
        tasks_paginator = api.get_tasks(project_id=project.id)
        existing_tasks = [task for page in tasks_paginator for task in page]
        existing_task_titles = {task.content for task in existing_tasks}
    except Exception as error:
        print(f"Error getting existing tasks: {error}")
        return

    # Add new tasks
    tasks_added_count = 0
    for task_title in tasks_to_sync:
        cleaned_title = task_title
        due_date = None
        priority = 1  # Default priority
        labels = []

        # Parse labels
        if cleaned_title.startswith("Flagged: "):
            labels.append("Flagged")
            cleaned_title = cleaned_title.replace("Flagged: ", "").strip()
        elif cleaned_title.startswith("Assigned: "):
            labels.append("Assigned")
            cleaned_title = cleaned_title.replace("Assigned: ", "").strip()

        # Parse due date
        due_match = re.search(r"\[Due: (\d{2}/\d{2}/\d{4})\]", cleaned_title)
        if due_match:
            date_str = due_match.group(1)
            due_date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            cleaned_title = cleaned_title.replace(due_match.group(0), "").strip()

        # Parse importance
        if "[Important]" in cleaned_title:
            priority = 4  # Urgent
            cleaned_title = cleaned_title.replace("[Important]", "").strip()

        if cleaned_title in existing_task_titles:
            print(f"Task '{cleaned_title}' already exists. Skipping.")
        else:
            print(f"Adding task '{cleaned_title}'...")
            try:
                api.add_task(
                    project_id=project.id,
                    content=cleaned_title,
                    due_string=due_date,
                    priority=priority,
                    labels=labels
                )
                print(f"Task '{cleaned_title}' added.")
                tasks_added_count += 1
            except Exception as error:
                print(f"Error adding task: {error}")
    
    # Close tasks in Todoist that are no longer present in the scraped file
    tasks_closed_count = 0
    for task in existing_tasks:
        # The content of the task in Todoist is the cleaned title.
        # We check if this cleaned title is present as a substring in any of the raw lines from the file.
        if not any(task.content in scraped_title for scraped_title in tasks_to_sync):
            print(f"Closing completed task: '{task.content}'")
            try:
                api.complete_task(task_id=task.id)
                tasks_closed_count += 1
            except Exception as error:
                print(f"Error closing task '{task.content}': {error}")

    print("\n--- Sync Summary ---")
    if tasks_added_count > 0:
        print(f"Added {tasks_added_count} new task(s).")
    else:
        print("No new tasks were added.")

    if tasks_closed_count > 0:
        print(f"Closed {tasks_closed_count} completed task(s).")
    else:
        print("No tasks were closed.")
    print("--------------------\n")


if __name__ == "__main__":
    main()