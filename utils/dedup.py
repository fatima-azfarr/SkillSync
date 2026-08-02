import json, os


def is_duplicate(listing, existing_listings):
    # Hash-based check (title + company): catches the same job posted
    # on different sites with different URLs.
    existing_hashes = {item["hash"] for item in existing_listings}
    if listing.hash in existing_hashes:
        return True

    # URL-based check: catches the same posting scraped again where the
    # company field came back different (empty, "Confidential", a typo'd
    # spelling, or a wrong value from a flaky selector) — same URL always
    # means same job, regardless of what company text was extracted.
    existing_urls = {item["url"] for item in existing_listings if item.get("url")}
    if listing.url and listing.url in existing_urls:
        return True

    return False