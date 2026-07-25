# SkillSync
### AI-Driven Internship & Tech Event Discovery Platform

SkillSync is a Final Year Project (FYP) that automatically collects internship and tech event listings from multiple platforms, processes them through a data pipeline, and will eventually rank them against a student's skill profile using a three-layer recommendation engine.

> **Current status:** Data pipeline and scraping layer complete (Week 1-2). ML/recommendation layer in development (FYP-I).

---

## The Problem

University students in tech struggle to find relevant internships and hackathons — opportunities are scattered across dozens of platforms with no central system. Existing tools use keyword search that ignores whether a student is actually qualified. No platform tells students which skills they're missing or highlights opportunities they're close to qualifying for.

## The Solution

SkillSync scrapes listings from six platforms on a scheduled basis, deduplicates them using SHA256 fingerprinting, and will eventually rank them against a student's skill profile using Content-Based Filtering (TF-IDF + cosine similarity), showing both matched opportunities and near-misses with exact skill gaps.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Scraping | Python, requests, BeautifulSoup4, Scrapy, Selenium |
| Data Pipeline | Python, hashlib (SHA256), json, threading |
| Backend (planned) | FastAPI, Motor, MongoDB |
| Frontend (planned) | React.js |
| DevOps (planned) | Docker, docker-compose |

---

## Project Structure

```
SkillSync/
├── utils/                      # Core data pipeline modules
│   ├── listing_schema.py       # Listings class — standardizes all scraper output
│   ├── dedup.py                # SHA256 hash-based duplicate detection
│   ├── file_utils.py           # Read/write listings to JSON
│   ├── logger.py               # Dual handler logging — terminal + file
│   └── data_pipeline_v1.py     # Full pipeline with ThreadPoolExecutor
├── scrapers/                   # One file per data source
│   └── mustaqbil_scrapper.py   # Mustakbil.com API scraper
├── Practice/                   # Learning demos (OOP, JSON, threading)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/fatima-azfarr/SkillSync.git
cd SkillSync

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Scrapers

Always run from the project root:

```bash
# Mustakbil.com scraper
python scrapers/mustaqbil_scrapper.py
```

Output is saved to `listings.json` in the project root. All activity is logged to `pipeline.log`.

---

## Data Pipeline Flow

```
Scraper pulls raw data from source
        ↓
Listings class standardizes into consistent schema
        ↓
SHA256 hash generated (title + company) for fingerprinting
        ↓
Duplicate check against existing listings
        ↓
New listing saved to listings.json
        ↓
All steps logged with timestamps
```

---

## Week-by-Week Progress

### Week 1 — Python Foundation & Data Pipeline
Built the core utility library:
- `listing_schema.py` — standardizes all scraper output. Every job from every site gets forced into the same shape with a SHA256 fingerprint for deduplication
- `dedup.py` — catches duplicates across sources using hash comparison
- `file_utils.py` — reads and writes listings to JSON with file existence handling
- `logger.py` — logs everything to terminal and file simultaneously with timestamps
- `data_pipeline_v1.py` — connects all four using `ThreadPoolExecutor` for parallel processing with `Lock()` for thread-safe writes

### Week 2 — Web Scraping
- Investigated Mustakbil.com network traffic using DevTools — discovered public REST API returning clean JSON (no BeautifulSoup or Selenium needed)
- Built `mustaqbil_scrapper.py` with User-Agent spoofing, pagination, 429 rate limit handling, and full pipeline integration
- **200 real job listings scraped and saved**

---

## Planned Modules (FYP-I)

- spaCy NER + skill lexicon → skill extraction from listing descriptions
- TF-IDF vectorization → domain classifier (AI, Web Dev, Cybersecurity, Data Science, Mobile)
- Cosine similarity CBF engine → matched (≥0.70) and near-miss (0.40–0.70) recommendations
- Jaccard skill gap analysis → missing skill badges
- Collaborative Filtering → peer-based discovery
- React dashboard → two-tier display with skill gap badges
- Notification system → alerts within one scraping cycle

---


