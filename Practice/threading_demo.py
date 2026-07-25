from concurrent.futures import ThreadPoolExecutor
import threading
import time
import random

# Shared list where all threads will store results
results = []

# Lock to protect shared data
lock = threading.Lock()

def scrape(url):
    print(f"Starting: {url}")

    # Simulate network delay (like waiting for a website)
    time.sleep(random.randint(1, 3))
    data = f"Data scraped from {url}"

    # Only one thread can append at a time
    with lock:
        results.append(data)
    print(f"Finished: {url}")
    return data

# List of websites

urls = [

    "rozee.pk",

    "mustakbil.com",

    "wuzzuf.net",

    "indeed.com",

    "linkedin.com",

    "glassdoor.com"

]

# Create a pool of 3 worker threads

with ThreadPoolExecutor(max_workers=6) as executor:
    returned_data = executor.map(scrape, urls)
print("\nReturned Data:")

for item in returned_data:
    print(item)

print("\nShared Results List:")

for item in results:
    print(item)