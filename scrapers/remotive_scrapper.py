import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests , json
from utils.listing_schema import Listings
from utils.dedup import is_duplicate
from utils.logger import logger
from utils.file_utils import  read_listings,write_listings


saved_listings = read_listings("listings.json")

#1-hit the API - send server an HTTP request
response = requests.get("https://remotive.com/api/remote-jobs")

#2-parse the json
api_data = response.json()


jobs = api_data["jobs"]

#3-loop thru each job
for job in jobs:

    listings = Listings (
        title = job["title"],
        company = job["company_name"],
        source = "remotive.com",
        skills = job["tags"],
        deadline = job["publication_date"],
        url = job["url"]
        
    )
    if is_duplicate(listings, saved_listings):
        logger.info(f"Skipped duplicate: {listings.title}")
    else:
        saved_listings.append(listings.to_dict())
        logger.info(f"Saved: {listings.title} - {listings.company}")
    
    
write_listings(saved_listings, "listings.json")
logger.info(f"Finished. Total listings saved: {len(saved_listings)}")


    
