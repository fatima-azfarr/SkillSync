import sys
import os
import re
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException

from utils.listing_schema import Listings
from utils.file_utils import read_listings, write_listings
from utils.dedup import is_duplicate
from utils.logger import logger


# ---------------------------------------
# Config
# ---------------------------------------

MAX_PAGES = 400
CHECKPOINT_FILE = "wuzzuf_checkpoint.txt"

# Strings that look like a location, not a company.
# Egyptian/Gulf job cards commonly show "Area, City, Country" or "City, Country"
# in a span with no distinguishing class — that's what was leaking into `company`.
LOCATION_PATTERN = re.compile(
    r",\s*(Egypt|Cairo|Giza|Alexandria|Saudi Arabia|Riyadh|United Arab Emirates|"
    r"Dubai|Qalubia|Sharqia|Monufya|United States|Canada)\s*$",
    re.IGNORECASE,
)


def is_location_like(text: str) -> bool:
    if LOCATION_PATTERN.search(text):
        return True
    # bare "Cairo, Egypt" / "Alexandria, Egypt" style with no company signal
    if text.count(",") >= 1 and any(
        city in text for city in ["Cairo", "Giza", "Alexandria", "Egypt", "Saudi Arabia"]
    ):
        return True
    return False


# ---------------------------------------
# Driver setup / teardown
# ---------------------------------------

def make_driver():
    d = uc.Chrome(
        headless=False,
        driver_executable_path="/Users/user/Documents/SkillSync/chromedriver",
    )
    d.maximize_window()
    return d


def load_checkpoint() -> int:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            content = f.read().strip()
            if content.isdigit():
                logger.info(f"Resuming from checkpoint: page {content}")
                return int(content)
    return 0


def save_checkpoint(page: int):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(page))


# ---------------------------------------
# Main scrape loop
# ---------------------------------------

saved_listings = read_listings("listings.json")
page = load_checkpoint()

driver = make_driver()

while page < MAX_PAGES:

    url = "https://wuzzuf.net/search/jobs" if page == 0 else f"https://wuzzuf.net/search/jobs?start={page}"
    logger.info(f"Opening {url}")

    # --- navigate, with one restart-and-retry on a dead session ---
    try:
        driver.get(url)
    except (InvalidSessionIdException, WebDriverException) as e:
        logger.error(f"Browser session died ({e}). Restarting driver and retrying page {page}.")
        try:
            driver.quit()
        except Exception:
            pass
        time.sleep(5)
        driver = make_driver()
        try:
            driver.get(url)
        except (InvalidSessionIdException, WebDriverException) as e2:
            logger.error(f"Retry failed too ({e2}). Stopping — resume later from checkpoint.")
            break

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/p/']"))
        )
    except Exception:
        logger.info("Reached last page.")
        break

    time.sleep(2)

    cards = driver.find_elements(By.XPATH, "//div[.//a[contains(@href,'/jobs/p/')]]")
    seen_urls = set()

    logger.info(f"Processing page {page + 1} ({len(cards)} cards found)")

    new_jobs = 0

    for card in cards:
        try:
            # ------------------------------
            # Job Link
            # ------------------------------
            links = card.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/p/']")
            if not links:
                continue

            job_link = None
            for link in links:
                if link.text.strip():
                    job_link = link
                    break
            if job_link is None:
                job_link = links[0]

            title = job_link.text.strip()
            if not title:
                continue

            job_url = job_link.get_attribute("href")
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            # ------------------------------
            # Company
            # ------------------------------
            company = "Confidential"

            company_links = card.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/careers/']")
            for c in company_links:
                text = c.text.strip().replace("-", "").strip()
                if text:
                    company = text
                    break

            # Fallback: scan spans, but reject anything location-shaped
            if company == "Confidential":
                spans = card.find_elements(By.TAG_NAME, "span")
                for span in spans:
                    txt = span.text.strip()
                    if (
                        txt
                        and txt != title
                        and len(txt) < 60
                        and "ago" not in txt.lower()
                        and "full time" not in txt.lower()
                        and "part time" not in txt.lower()
                        and not is_location_like(txt)
                    ):
                        company = txt
                        break

            listing = Listings(
                title=title,
                company=company,
                source="wuzzuf.net",
                skills=[],
                deadline=None,
                url=job_url,
            )

            if is_duplicate(listing, saved_listings):
                logger.info(f"Skipped duplicate: {title} - {company}")
                continue

            saved_listings.append(listing.to_dict())
            new_jobs += 1
            logger.info(f"Saved: {title} - {company}")

        except Exception as e:
            logger.error(f"Skipping job: {e}")

    write_listings(saved_listings, "listings.json")
    logger.info(f"Finished page {page + 1}. Added {new_jobs} new jobs.")

    page += 1
    save_checkpoint(page)

    time.sleep(3)

try:
    driver.quit()
except Exception:
    pass

write_listings(saved_listings, "listings.json")
if os.path.exists(CHECKPOINT_FILE):
    os.remove(CHECKPOINT_FILE)

logger.info(f"Finished scraping. Total listings: {len(saved_listings)}")