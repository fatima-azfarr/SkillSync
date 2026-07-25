import requests
import time  # add this import at top

from utils.listing_schema import Listings
from utils.dedup import is_duplicate
from utils.file_utils import read_listings, write_listings
from utils.logger import logger

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

page = 1
saved_listings = read_listings("listings.json")

while True:
    try:
        response = requests.get(
            f"https://api-public.mustakbil.com/ws/jobs/search/?countryid=162&page={page}",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            logger.warning("Rate limited. Waiting 10 seconds...")
            time.sleep(10)
            continue  # retry same page, don't increment page
        else:
            raise

    api_data = response.json()
    jobs = api_data.get("list", [])

    if not jobs or not api_data.get("hasMore", False):
        break

    logger.info(f"Processing page {page} ({len(jobs)} jobs found)")

    for job in jobs:
        listing = Listings(
            title=job["title"],
            company=job["company"],
            source="mustakbil.com",
            skills=[],
            deadline=job.get("lastDate"),
            url=f"https://www.mustakbil.com/jobs/job/{job['id']}",
        )

        if is_duplicate(listing, "listings.json"):
            logger.info(f"Skipped duplicate: {listing.title}")
        else:
            saved_listings.append(listing.to_dict())
            logger.info(f"Saved: {listing.title} - {listing.company}")

    time.sleep(1)  # 1 second between every page
    page += 1

write_listings(saved_listings, "listings.json")
logger.info(f"Finished. Total listings saved: {len(saved_listings)}")