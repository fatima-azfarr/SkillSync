from concurrent.futures import ThreadPoolExecutor
import threading
from listing_schema import Listings
from dedup import is_duplicate
from file_utils import read_listings, write_listings
from logger import logger

# Lock because multiple threads will access listings.json
lock = threading.Lock()

fake_listings = [
    Listings("Python Developer Intern", "Systems Limited", "rozee.pk",
             ["Python", "Django"], "2025-08-01", "rozee.pk/job/1"),

    Listings("React Frontend Intern", "Arbisoft", "mustakbil.com",
             ["React", "JavaScript"], "2025-08-15", "mustakbil.com/job/2"),

    Listings("Python Developer Intern", "Systems Limited", "mustakbil.com",
             ["Python", "Django"], "2025-08-01", "mustakbil.com/job/1"),

    Listings("Data Analyst Intern", "Netsol", "rozee.pk",
             ["Python", "SQL", "PowerBI"], "2025-09-01", "rozee.pk/job/3"),
]


def process_listing(item):
    """Process one listing."""

    # Only one thread should read/write the JSON file at a time
    with lock:
        if is_duplicate(item, "listings.json"):
            logger.info(f"Skipped duplicate: {item.title} - {item.company}")
            return
        data = read_listings("listings.json")
        data.append(item.to_dict())
        write_listings(data, "listings.json")

        logger.info(f"Saved: {item.title} - {item.company}")


# Create a pool of 4 worker threads
with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_listing, fake_listings)

print("Finished processing listings.")