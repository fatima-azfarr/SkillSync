import json, os

def is_duplicate(listing, existing_listings):
    existing_hashes = {item["hash"] for item in existing_listings}
    return listing.hash in existing_hashes