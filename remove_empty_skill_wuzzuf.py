import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_utils import read_listings, write_listings
from utils.logger import logger


# ---------------------------------------------------------
# Same approach as remove_empty_skill_rozee.py — removes Wuzzuf
# entries with no skills captured, so re-running wuzzuf_scrapper.py
# will no longer see them as duplicates and will re-save them,
# this time picking up skills via the now-fixed a.css-5x9pm1 selector.
#
# Only touches wuzzuf.net rows. Every other source is left as-is.
# ---------------------------------------------------------

INPUT_FILE = "listings.json"
BACKUP_FILE = "listings_before_wuzzuf_backfill.json"
TARGET_SOURCE = "wuzzuf.net"


def main():
    if os.path.exists(INPUT_FILE):
        shutil.copy(INPUT_FILE, BACKUP_FILE)
        logger.info(f"Backed up {INPUT_FILE} -> {BACKUP_FILE}")

    listings = read_listings(INPUT_FILE)
    logger.info(f"Loaded {len(listings)} total listings")

    kept = []
    removed = 0

    for entry in listings:
        is_target_source = entry.get("source") == TARGET_SOURCE
        has_no_skills = not entry.get("skills")

        if is_target_source and has_no_skills:
            removed += 1
            continue

        kept.append(entry)

    logger.info(f"Removed {removed} Wuzzuf entries with empty skills")
    logger.info(f"Remaining listings: {len(kept)}")

    write_listings(kept, INPUT_FILE)
    logger.info(f"{INPUT_FILE} updated. Re-run wuzzuf_scrapper.py to backfill the removed entries with skills.")


if __name__ == "__main__":
    main()