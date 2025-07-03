import asyncio
from src.scraper import main as run_scraper
from src.syncer import main as run_syncer

async def main():
    print("Starting scraper...")
    await run_scraper()
    print("Scraping complete. Starting sync...")
    run_syncer()
    print("Sync complete.")

if __name__ == "__main__":
    asyncio.run(main())