import sys
import os
import re
import time
import random

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

MAX_PAGES = 400          # safety ceiling, same role as Wuzzuf's MAX_PAGES
JOBS_PER_PAGE = 20       # Rozee's fpn offset step, confirmed from pagination
CHECKPOINT_FILE = "rozee_checkpoint.txt"

# Pacing: deliberately more cautious than Wuzzuf (3s) since Rozee has
# active CAPTCHA infrastructure even though it hasn't triggered yet.
MIN_DELAY = 6
MAX_DELAY = 8

# Signals that a CAPTCHA / bot-check page loaded instead of real results.
# Checked after every page load, before we try to parse any cards.
CAPTCHA_INDICATORS = [
    "verify you are human",
    "unusual traffic",
    "are you a robot",
    "complete the security check",
    "checking your browser",
]


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
                logger.info(f"Resuming from checkpoint: offset {content}")
                return int(content)
    return 0


def save_checkpoint(offset: int):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(offset))


def page_has_captcha(driver) -> bool:
    """Cheap check: look at lowercased page source for known CAPTCHA markers."""
    try:
        html = driver.page_source.lower()
    except Exception:
        return False
    return any(marker in html for marker in CAPTCHA_INDICATORS)


# ---------------------------------------
# Main scrape loop
# ---------------------------------------

saved_listings = read_listings("listings.json")
offset = load_checkpoint()

driver = make_driver()

page_num = 0

while offset < MAX_PAGES * JOBS_PER_PAGE:

    url = f"https://www.rozee.pk/job/jsearch/q/all/fpn/{offset}"
    logger.info(f"Opening {url}")

    # --- navigate, with one restart-and-retry on a dead session ---
    try:
        driver.get(url)
    except (InvalidSessionIdException, WebDriverException) as e:
        logger.error(f"Browser session died ({e}). Restarting driver and retrying offset {offset}.")
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
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#jobs.jlist"))
        )
    except Exception:
        logger.info("Job list container never appeared — reached last page or site changed layout.")
        break

    time.sleep(2)

    # --- CAPTCHA check before we trust anything on this page ---
    if page_has_captcha(driver):
        logger.error(
            f"CAPTCHA detected at offset {offset}. Stopping scrape — "
            f"checkpoint saved, resolve manually and re-run to resume."
        )
        break

    page_num += 1

    # Only direct .job children of #jobs — this also naturally excludes
    # the interspersed div.adBanner.flListHd elements at the same level.
    cards = driver.find_elements(By.CSS_SELECTOR, "div#jobs.jlist > div.job")

    logger.info(f"Processing offset {offset} ({len(cards)} cards found)")

    new_jobs = 0

    for card in cards:
        try:
            # ------------------------------
            # Title + URL
            # ------------------------------
            title_link = card.find_element(By.CSS_SELECTOR, "div.jhead h3.s-18 a")
            title = title_link.get_attribute("title") or title_link.text.strip()
            title = title.strip()
            job_url = title_link.get_attribute("href")

            if not title or not job_url:
                continue

            # ------------------------------
            # Company / City / Country
            # ------------------------------
            company = "Confidential"
            location_parts = []

            try:
                cname_links = card.find_elements(
                    By.CSS_SELECTOR, "div.jhead div.cname bdi a.display-inline"
                )
                texts = []
                for c in cname_links:
                    # Strip common invisible characters (non-breaking space,
                    # zero-width space) that survive .strip() and cause
                    # empty-looking fragments like "Peshawar, , Pakistan".
                    raw = c.text.replace("\u200b", "").replace("\xa0", " ").strip()
                    cleaned = raw.rstrip(",").strip()
                    # Only keep fragments with actual letters/digits — filters
                    # out anything that's invisible-but-truthy.
                    if cleaned and re.search(r"\w", cleaned, re.UNICODE):
                        texts.append(cleaned)

                if texts:
                    company = texts[0]
                    location_parts = texts[1:]
            except Exception:
                pass

            location = ", ".join(location_parts) if location_parts else ""

            # ------------------------------
            # Date + Experience
            # ------------------------------
            deadline = None
            try:
                date_el = card.find_element(
                    By.CSS_SELECTOR, "div.jfooter span[data-original-title]"
                )
                deadline = date_el.get_attribute("data-original-title") or date_el.text.strip()
            except Exception:
                pass

            experience = None
            try:
                exp_el = card.find_element(By.CSS_SELECTOR, "div.jfooter span.func-area.uptos")
                experience = exp_el.text.strip()
            except Exception:
                pass

            # ------------------------------
            # Skill tags (shown as pill buttons in the card footer)
            # ------------------------------
            skills = []
            try:
                tag_els = card.find_elements(
                    By.CSS_SELECTOR, "div.jfooter .job-dtl span.label"
                )
                skills = [t.text.strip() for t in tag_els if t.text.strip()]
            except Exception:
                pass

            listing = Listings(
                title=title,
                company=company,
                source="rozee.pk",
                skills=skills,
                deadline=deadline,
                url=job_url,
            )

            if is_duplicate(listing, saved_listings):
                logger.info(f"Skipped duplicate: {title} - {company}")
                continue

            saved_listings.append(listing.to_dict())
            new_jobs += 1
            logger.info(f"Saved: {title} - {company} ({location})")

        except Exception as e:
            logger.error(f"Skipping job: {e}")

    write_listings(saved_listings, "listings.json")
    logger.info(f"Finished offset {offset}. Added {new_jobs} new jobs.")

    # If a page comes back with zero cards, we've likely run past the last page.
    if len(cards) == 0:
        logger.info("No cards found on this page — assuming end of results.")
        break

    offset += JOBS_PER_PAGE
    save_checkpoint(offset)

    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    logger.info(f"Sleeping {delay:.1f}s before next page.")
    time.sleep(delay)

try:
    driver.quit()
except Exception:
    pass

write_listings(saved_listings, "listings.json")
if os.path.exists(CHECKPOINT_FILE):
    os.remove(CHECKPOINT_FILE)

logger.info(f"Finished scraping. Total listings: {len(saved_listings)}")