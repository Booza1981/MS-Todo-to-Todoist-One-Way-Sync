import asyncio
import os
import sys
from playwright.async_api import async_playwright, TimeoutError, Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
AUTH_FILE = "auth.json"
OUTPUT_FILE = os.getenv("INPUT_FILE")

async def scrape_task_list(page, list_name, url=None, click_selector=None, wait_for_text_str=None, task_prefix=""):
    """A generic function to scrape tasks from a specific list."""
    print(f"Scraping tasks from '{list_name}'...")
    try:
        if url:
            await page.goto(url)
        elif click_selector:
            await page.click(click_selector)
            if wait_for_text_str:
                await page.wait_for_selector(f'span:has-text("{wait_for_text_str}")', timeout=15000)

        task_item_selector = '.grid-row:not(.row-group)'
        await page.wait_for_selector(task_item_selector, timeout=10000)
        
        task_elements = await page.query_selector_all(task_item_selector)
        
        tasks = []
        for element in task_elements:
            title_element = await element.query_selector('div[aria-colindex="2"]')
            task_title = ""
            if title_element:
                task_title = (await title_element.inner_text()).strip()

            if not task_title:
                continue

            due_date_text = ""
            due_date_element = await element.query_selector('div[aria-colindex="3"]')
            if due_date_element:
                due_date_text = (await due_date_element.inner_text()).strip()

            is_important = False
            importance_element = await element.query_selector('div[aria-colindex="4"]')
            if importance_element:
                importance_label = await importance_element.get_attribute('aria-label') or ""
                if "important" in importance_label.lower():
                    is_important = True

            final_title = task_title
            if due_date_text:
                final_title += f" [Due: {due_date_text}]"
            if is_important:
                final_title += " [Important]"
            
            if task_prefix:
                tasks.append(f"{task_prefix}: {final_title}")
            else:
                tasks.append(final_title)
        
        print(f"Found {len(tasks)} tasks in '{list_name}'.")
        return tasks
    except TimeoutError:
        print(f"Timeout while waiting for task list '{list_name}' to load. The website UI may have changed.")
        return []
    except Error as e:
        print(f"A Playwright-specific error occurred while scraping '{list_name}': {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while scraping '{list_name}': {e}")
        return []


async def main():
    """
    Main function to run the scraper. It uses a saved authentication state
    to log in automatically. If the auth state doesn't exist, it prompts
    the user for a manual login to create it.

    Run with "python scraper.py --setup" for the initial login.
    """
    async with async_playwright() as p:
        # By default, run in headless mode. Use --setup flag to run with a visible browser.
        is_headless = '--setup' not in sys.argv

        if os.path.exists(AUTH_FILE):
            # --- Automatic Login ---
            browser = await p.chromium.launch(headless=is_headless)
            context = await browser.new_context(storage_state=AUTH_FILE)
            page = await context.new_page()
            await page.goto("https://to-do.office.com/tasks/inbox")
            print("Logged in automatically using saved session.")
            await page.screenshot(path="screenshots/login_attempt.png")

            tasks = await scrape_task_list(
                page,
                list_name="Tasks",
                url="https://to-do.office.com/tasks/inbox"
            )
            flagged_emails = await scrape_task_list(
                page,
                list_name="Flagged email",
                click_selector='#flagged',
                wait_for_text_str="Flagged email",
                task_prefix="Flagged"
            )
            assigned_tasks = await scrape_task_list(
                page,
                list_name="Assigned to me",
                click_selector='#assigned_to_me',
                wait_for_text_str="Assigned to me",
                task_prefix="Assigned"
            )

            all_tasks = tasks + flagged_emails + assigned_tasks
            print(f"Found a total of {len(all_tasks)} items.")
            
            if all_tasks:
                print(f"--- Writing {len(all_tasks)} tasks to {OUTPUT_FILE} ---")
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    for task_title in all_tasks:
                        f.write(f"{task_title}\n")
                print("--- Done ---")


        else:
            # --- First-Time Manual Login ---
            browser = await p.chromium.launch(headless=is_headless)
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