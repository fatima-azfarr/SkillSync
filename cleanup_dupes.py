import re
import hashlib
import collections
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_utils import read_listings, write_listings
from utils.logger import logger


# ---------------------------------------------------------
# Why this exists:
#
# dedup checks by hash, and hash = sha256(title + company).
# When the scraper's company-extraction is flaky (empty string,
# "Confidential" placeholder, or a wrong value grabbed from a
# neighboring card), the SAME job posting (same url) ends up
# saved multiple times under different hashes.
#
# This script finds every url that appears more than once,
# picks the single best company value out of the candidates,
# and keeps only one row per url.
# ---------------------------------------------------------

PLACEHOLDER_COMPANIES = {"", "confidential"}


def slug_tokens(url):
    """Pull word-like tokens out of the last path segment of a job URL.
    Many job boards (Wuzzuf in particular) embed the company name in
    the slug, e.g. .../senior-engineer-leeds-fit-out-giza-egypt
    """
    match = re.search(r"/([a-z0-9\-]+)(?:$|\?)", url.lower())
    if not match:
        return set()
    slug = match.group(1)
    return set(t for t in re.split(r"[-_/]+", slug) if len(t) > 2)


def company_tokens(company):
    return set(t for t in re.split(r"[^a-z0-9]+", company.lower()) if len(t) > 2)


def score_candidate(company, url_tokens):
    """Higher score = more overlap between company name and URL slug.
    -1 means placeholder or no matchable words at all.
    """
    if company.strip().lower() in PLACEHOLDER_COMPANIES:
        return -1
    tokens = company_tokens(company)
    if not tokens:
        return -1
    return len(tokens & url_tokens)


def pick_best_company(entries):
    """Return (chosen_company, reason_string) for a group of duplicate
    entries sharing the same url.
    """
    url = entries[0]["url"]
    url_tokens = slug_tokens(url)

    scored = [(score_candidate(e["company"], url_tokens), e["company"]) for e in entries]
    best_score = max(s for s, _ in scored)

    if best_score >= 0:
        candidates = [c for s, c in scored if s == best_score]
        if len(candidates) == 1:
            return candidates[0], f"slug_match(score={best_score})"
        # tie among equally-good slug matches — pick whichever recurs most
        counts = collections.Counter(candidates)
        return counts.most_common(1)[0][0], f"slug_match_tie(score={best_score})"

    # Nothing matched the URL at all (e.g. sources whose slugs don't
    # embed the company name). Fall back to the most common non-placeholder
    # value across the duplicate copies.
    non_placeholder = [
        e["company"] for e in entries
        if e["company"].strip().lower() not in PLACEHOLDER_COMPANIES
    ]
    if non_placeholder:
        counts = collections.Counter(non_placeholder)
        return counts.most_common(1)[0][0], "fallback:most_common_nonplaceholder"

    # every candidate was a placeholder — nothing better to do than keep one
    return entries[0]["company"], "fallback:all_placeholder_kept_first"


def make_hash(title, company):
    fingerprint = f"{title.lower().strip()}{company.lower().strip()}"
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def clean_duplicates(listings):
    by_url = collections.defaultdict(list)
    for entry in listings:
        by_url[entry.get("url")].append(entry)

    cleaned = []
    report_lines = []
    changed_groups = 0

    for url, entries in by_url.items():
        if len(entries) == 1:
            cleaned.append(entries[0])
            continue

        changed_groups += 1
        best_company, reason = pick_best_company(entries)

        # keep the row that already carries the winning company value,
        # so its deadline/skills fields (if they varied too) come along
        base = next((e for e in entries if e["company"] == best_company), entries[0])

        merged = dict(base)
        merged["company"] = best_company
        merged["hash"] = make_hash(merged["title"], best_company)
        cleaned.append(merged)

        report_lines.append(f"URL: {url}")
        report_lines.append(f"  candidates: {[e['company'] for e in entries]}")
        report_lines.append(f"  chosen:     {best_company!r}  ({reason})")
        report_lines.append("")

    return cleaned, report_lines, changed_groups


if __name__ == "__main__":
    INPUT_FILE = "listings.json"
    REPORT_FILE = "cleanup_report.txt"

    listings = read_listings(INPUT_FILE)
    logger.info(f"Loaded {len(listings)} listings from {INPUT_FILE}")

    cleaned, report_lines, changed_groups = clean_duplicates(listings)

    removed = len(listings) - len(cleaned)
    logger.info(f"Duplicate groups resolved: {changed_groups}")
    logger.info(f"Rows removed: {removed}")
    logger.info(f"Final count: {len(cleaned)}")

    with open(REPORT_FILE, "w") as f:
        f.write(f"Input rows: {len(listings)}\n")
        f.write(f"Output rows: {len(cleaned)}\n")
        f.write(f"Duplicate groups resolved: {changed_groups}\n")
        f.write(f"Rows removed: {removed}\n\n")
        f.write("=" * 60 + "\n\n")
        f.write("\n".join(report_lines))

    logger.info(f"Full decision log written to {REPORT_FILE} — review before trusting the output.")

    write_listings(cleaned, INPUT_FILE)
    logger.info(f"{INPUT_FILE} updated in place.")