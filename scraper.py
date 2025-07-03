import asyncio
import os
from playwright.async_api import async_playwright
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Your Todoist API token. It's recommended to set this as an environment variable.
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

# The name of the Todoist project to sync tasks to.
TODOIST_PROJECT_NAME = "Synced Work Tasks"

AUTH_FILE = "auth.json"

async def get_tasks(page):
    """Scrapes tasks from the main 'Tasks' list."""
    print("Navigating to the main 'Tasks' section...")
    await page.goto("https://to-do.office.com/tasks/inbox")
    
    task_item_selector = '.grid-row:not(.row-group)'
    
    try:
        await page.wait_for_selector(task_item_selector, timeout=10000)
        
        task_elements = await page.query_selector_all(task_item_selector)
        
        tasks = []
        for element in task_elements:
            # Get title
            title_element = await element.query_selector('div[aria-colindex="2"]')
            task_title = ""
            if title_element:
                task_title = (await title_element.inner_text()).strip()

            if not task_title:
                continue

            # Get due date
            due_date_text = ""
            due_date_element = await element.query_selector('div[aria-colindex="3"]')
            if due_date_element:
                due_date_text = (await due_date_element.inner_text()).strip()

            # Get importance
            is_important = False
            importance_element = await element.query_selector('div[aria-colindex="4"]')
            if importance_element:
                importance_label = await importance_element.get_attribute('aria-label') or ""
                if "important" in importance_label.lower():
                    is_important = True

            # Construct the final title
            final_title = task_title
            if due_date_text:
                final_title += f" [Due: {due_date_text}]"
            if is_important:
                final_title += " [Important]"
            
            tasks.append({"title": final_title})
        
        print(f"Found {len(tasks)} tasks in 'Tasks'.")
        return tasks
    except Exception:
        print("Could not find any tasks in the 'Tasks' section or the view is empty.")
        return []

async def get_flagged_emails(page):
    """Scrapes tasks from the 'Flagged email' section."""
    print("Navigating to 'Flagged email' section...")
    try:
        await page.click('#flagged')
        
        await page.wait_for_selector('span:has-text("Flagged email")', timeout=15000)
        print("Flagged email list loaded. Scraping tasks...")

        task_item_selector = '.grid-row:not(.row-group)'
        await page.wait_for_selector(task_item_selector, timeout=10000)
        
        task_elements = await page.query_selector_all(task_item_selector)
        
        tasks = []
        for element in task_elements:
            # Get title
            title_element = await element.query_selector('div[aria-colindex="2"]')
            task_title = ""
            if title_element:
                task_title = (await title_element.inner_text()).strip()

            if not task_title:
                continue

            # Get due date
            due_date_text = ""
            due_date_element = await element.query_selector('div[aria-colindex="3"]')
            if due_date_element:
                due_date_text = (await due_date_element.inner_text()).strip()

            # Get importance
            is_important = False
            importance_element = await element.query_selector('div[aria-colindex="4"]')
            if importance_element:
                importance_label = await importance_element.get_attribute('aria-label') or ""
                if "important" in importance_label.lower():
                    is_important = True

            # Construct the final title
            final_title = task_title
            if due_date_text:
                final_title += f" [Due: {due_date_text}]"
            if is_important:
                final_title += " [Important]"
            
            tasks.append({"title": f"Flagged: {final_title}"})
        
        print(f"Found {len(tasks)} tasks in 'Flagged email'.")
        return tasks
    except Exception:
        print("Could not find any tasks in 'Flagged email' or the view is empty.")
        return []

async def get_assigned_tasks(page):
    """Scrapes tasks from the 'Assigned to me' section."""
    print("Navigating to 'Assigned to me' section...")
    try:
        await page.click('#assigned_to_me')

        await page.wait_for_selector('span:has-text("Assigned to me")', timeout=15000)
        print("Assigned to me list loaded. Scraping tasks...")

        task_item_selector = '.grid-row:not(.row-group)'
        await page.wait_for_selector(task_item_selector, timeout=10000)
        
        task_elements = await page.query_selector_all(task_item_selector)
        
        tasks = []
        for element in task_elements:
            # Get title
            title_element = await element.query_selector('div[aria-colindex="2"]')
            task_title = ""
            if title_element:
                task_title = (await title_element.inner_text()).strip()

            if not task_title:
                continue

            # Get due date
            due_date_text = ""
            due_date_element = await element.query_selector('div[aria-colindex="3"]')
            if due_date_element:
                due_date_text = (await due_date_element.inner_text()).strip()

            # Get importance
            is_important = False
            importance_element = await element.query_selector('div[aria-colindex="4"]')
            if importance_element:
                importance_label = await importance_element.get_attribute('aria-label') or ""
                if "important" in importance_label.lower():
                    is_important = True

            # Construct the final title
            final_title = task_title
            if due_date_text:
                final_title += f" [Due: {due_date_text}]"
            if is_important:
                final_title += " [Important]"
            
            tasks.append({"title": f"Assigned: {final_title}"})
        
        print(f"Found {len(tasks)} tasks in 'Assigned to me'.")
        return tasks
    except Exception:
        print("Could not find any tasks in 'Assigned to me' or the view is empty.")
        return []

def _sync_logic(tasks_to_sync):
    """
    Contains the actual synchronous logic to be run in a separate thread.
    This prevents blocking the asyncio event loop.
    """
    api = TodoistAPI(TODOIST_API_TOKEN)
    
    # Find project
    try:
        projects = api.get_projects()
        project = next((p for p in projects if p.name == TODOIST_PROJECT_NAME), None)
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
        existing_tasks = api.get_tasks(project_id=project.id)
        existing_task_titles = {task.content for task in existing_tasks}
    except Exception as error:
        print(f"Error getting existing tasks: {error}")
        return

    # Add new tasks
    tasks_added_count = 0
    for task_title in tasks_to_sync:
        if task_title in existing_task_titles:
            print(f"Task '{task_title}' already exists. Skipping.")
        else:
            print(f"Adding task '{task_title}'...")
            try:
                api.add_task(project_id=project.id, content=task_title)
                print(f"Task '{task_title}' added.")
                tasks_added_count += 1
            except Exception as error:
                print(f"Error adding task: {error}")
    
    if tasks_added_count > 0:
        print(f"Sync complete. Added {tasks_added_count} new task(s).")
    else:
        print("Sync complete. No new tasks were added.")


async def sync_to_todoist(tasks_to_sync):
    """
    Runs the synchronous Todoist sync logic in a separate thread to avoid
    blocking the asyncio event loop.
    """
    print("Running Todoist sync in a separate thread...")
    await asyncio.to_thread(_sync_logic, tasks_to_sync)


async def main():
    """
    Main function to run the scraper. It uses a saved authentication state
    to log in automatically. If the auth state doesn't exist, it prompts
    the user for a manual login to create it.
    """
    async with async_playwright() as p:
        if os.path.exists(AUTH_FILE):
            # --- Automatic Login ---
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state=AUTH_FILE)
            page = await context.new_page()
            await page.goto("https://to-do.office.com/tasks/inbox")
            print("Logged in automatically using saved session.")

            tasks = await get_tasks(page)
            flagged_emails = await get_flagged_emails(page)
            assigned_tasks = await get_assigned_tasks(page)

            all_tasks = tasks + flagged_emails + assigned_tasks
            print(f"Found a total of {len(all_tasks)} items.")
            
            if all_tasks:
                print("--- Scraped Tasks ---")
                for task in all_tasks:
                    print(f"- {task['title']}")
                print("---------------------")
                
                # Sync the scraped tasks to Todoist
                if not TODOIST_API_TOKEN:
                    print("ERROR: TODOIST_API_TOKEN environment variable not set.")
                    print("Skipping Todoist sync.")
                else:
                    task_titles = [task['title'] for task in all_tasks]
                    await sync_to_todoist(task_titles)


        else:
            # --- First-Time Manual Login ---
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://to-do.office.com/tasks/")

            print("=" * 70)
            print("FIRST-TIME SETUP: Please log in to your work account in the browser.")
            print("After you are successfully logged in, press Enter in this terminal.")
            print("=" * 70)

            input()  # Wait for the user to press Enter

            await context.storage_state(path=AUTH_FILE)
            print(f"Authentication state saved to '{AUTH_FILE}'.")
            print("You can now run the script again for automatic scraping.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())