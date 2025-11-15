import requests
import time
import random
from bs4 import BeautifulSoup
import pathlib
import json

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"

# Create data/raw if not exists
DATA_RAW.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.indeed.com/jobs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def get_search_url(query="data analyst", location="California", start=0):
    return f"{BASE_URL}?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}&start={start}"

def scrape_search_page(query, location, start=0):
    url = get_search_url(query, location, start)
    print(f"Requesting URL: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("❌ Blocked or error:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def extract_job_cards(soup):
    # Indeed job card wrapper
    return soup.find_all("div", class_="cardOutline")


def parse_job_card(card):
    title = card.find("h2", class_="jobTitle")
    title = title.get_text(strip=True) if title else None

    company = card.find("span", class_="companyName")
    company = company.get_text(strip=True) if company else None

    location = card.find("div", class_="companyLocation")
    location = location.get_text(strip=True) if location else None

    salary = card.find("div", class_="salary-snippet")
    salary = salary.get_text(strip=True) if salary else None

    return {
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
    }


def scrape_jobs(query, location, pages=2, save_folder=DATA_RAW):
    save_path = pathlib.Path(save_folder)
    save_path.mkdir(parents=True, exist_ok=True)

    results = []

    for p in range(pages):
        print(f"\n🔎 Scraping page {p+1}/{pages} for {location}...")
        soup = scrape_search_page(query, location, start=p * 10)
        if soup is None:
            continue

        cards = extract_job_cards(soup)

        for card in cards:
            job = parse_job_card(card)
            results.append(job)

        # Random sleep to avoid getting blocked
        time.sleep(random.uniform(1.5, 3.5))

    # Save JSON
    outfile = save_path / f"{location.lower().replace(' ', '_')}_jobs.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Saved {len(results)} jobs for {location} → {outfile}")
    return results


if __name__ == "__main__":
    print("📁 Project root:", PROJECT_ROOT)
    print("📁 Saving raw data to:", DATA_RAW)

    scrape_jobs("data analyst", "California", pages=3, save_folder=DATA_RAW)
    scrape_jobs("data analyst", "New York", pages=3, save_folder=DATA_RAW)
