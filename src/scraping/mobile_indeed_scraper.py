import requests
from bs4 import BeautifulSoup
import json
import pathlib
import time
import random

# ----------------------------
# Path setup
# ----------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

# ----------------------------
# User agent rotation (avoid blocking)
# ----------------------------
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6)",
    "Mozilla/5.0 (iPad; CPU OS 15_6)",
]


def get_soup(url):
    """Fetch a URL and return BeautifulSoup object."""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"⚠️  Failed request {r.status_code}: {url}")
        return None

    return BeautifulSoup(r.text, "html.parser")


def parse_job_card(card):
    """Extract job info from a single mobile Indeed job card."""
    # Title
    title_tag = card.find("h2")
    title = title_tag.text.strip() if title_tag else None

    # Company
    company_tag = card.find("span", class_="companyName")
    company = company_tag.text.strip() if company_tag else None

    # Location
    loc_tag = card.find("div", class_="companyLocation")
    location = loc_tag.text.strip() if loc_tag else None

    # Salary
    salary_tag = card.find("div", class_="salary-snippet")
    salary = salary_tag.text.strip() if salary_tag else None

    # Link
    link_tag = card.find("a", href=True)
    job_url = None
    if link_tag:
        href = link_tag["href"]
        if href.startswith("/"):
            job_url = "https://www.indeed.com" + href
        else:
            job_url = href

    return {
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "url": job_url,
    }


def scrape_mobile_indeed(query, location, pages=3, delay=2):
    """Scrape multiple pages of Indeed mobile job listings."""
    results = []

    for p in range(pages):
        start = p * 10
        url = f"https://www.indeed.com/m/jobs?q={query}&l={location}&start={start}"

        print(f"\n🔎 Scraping {url}")
        soup = get_soup(url)
        if not soup:
            continue

        cards = soup.find_all("div", class_="job")

        print(f"   → Found {len(cards)} job cards on this page")

        for c in cards:
            job = parse_job_card(c)
            results.append(job)

        time.sleep(delay + random.uniform(0.5, 1.5))

    # Save results
    outfile = DATA_RAW / f"{location.lower().replace(' ', '_')}_mobile_jobs.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"\n✅ Saved {len(results)} jobs → {outfile}")

    return results


if __name__ == "__main__":
    scrape_mobile_indeed("data+analyst", "California", pages=5)
    scrape_mobile_indeed("data+analyst", "New+York", pages=5)
