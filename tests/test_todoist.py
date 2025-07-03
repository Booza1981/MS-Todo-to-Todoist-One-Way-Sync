import os
from todoist_api_python.api import TodoistAPI

# --- Synchronous Helper Functions ---

def find_project_by_name(api, project_name):
    """Finds a project by its name using the synchronous API."""
    print(f"Searching for project: '{project_name}'")
    try:
        projects = api.get_projects()
        for project in projects:
            if project.name == project_name:
                print(f"Found project: '{project.name}' (ID: {project.id})")
                return project
    except Exception as error:
        print(f"Error finding project: {error}")
    print(f"Project '{project_name}' not found.")
    return None

def find_task_by_title(api, project_id, task_title):
    """Finds a task by its title within a specific project using the synchronous API."""
    print(f"Searching for task: '{task_title}' in project {project_id}")
    try:
        tasks = api.get_tasks(project_id=project_id)
        for task in tasks:
            if task.content == task_title:
                print(f"Found task: '{task.content}' (ID: {task.id})")
                return task
    except Exception as error:
        print(f"Error finding task: {error}")
    print(f"Task '{task_title}' not found.")
    return None

# --- Main Execution Logic ---

def main():
    """Main function to demonstrate finding a project and a task."""
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        print("ERROR: TODOIST_API_TOKEN environment variable not set.")
        print("Please set it before running the script.")
        return

    api = TodoistAPI(api_token)

    # 1. Find the project named "MSFT-Sync"
    project_to_find = "MSFT-Sync"
    project = find_project_by_name(api, project_to_find)

    if project:
        # 2. If project is found, search for a sample task within it
        task_to_find = "My Test Task"
        task = find_task_by_title(api, project.id, task_to_find)
        
        if task:
            print(f"\nSUCCESS: Task '{task.content}' was found in project '{project.name}'.")
        else:
            print(f"\nINFO: Task '{task_to_find}' was not found in project '{project.name}'.")

if __name__ == "__main__":
    main()