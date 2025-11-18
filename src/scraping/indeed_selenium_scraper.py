from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import json
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

def scrape_indeed(query, location, pages=3):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    results = []

    for p in range(pages):
        url = f"https://www.indeed.com/jobs?q={query}&l={location}&start={p*10}"
        print("Scraping:", url)
        driver.get(url)
        time.sleep(2)   # wait for page to load

        cards = driver.find_elements(By.CLASS_NAME, "cardOutline")

        for c in cards:
            try:
                title = c.find_element(By.CLASS_NAME, "jobTitle").text
            except:
                title = None

            try:
                company = c.find_element(By.CLASS_NAME, "companyName").text
            except:
                company = None

            try:
                location_text = c.find_element(By.CLASS_NAME, "companyLocation").text
            except:
                location_text = None

            try:
                salary = c.find_element(By.CLASS_NAME, "salary-snippet").text
            except:
                salary = None

            results.append({
                "title": title,
                "company": company,
                "location": location_text,
                "salary": salary,
            })

        time.sleep(1.5)

    driver.quit()

    outfile = DATA_RAW / f"{location.lower().replace(' ', '_')}_jobs.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"Saved {len(results)} jobs → {outfile}")
    return results


if __name__ == "__main__":
    scrape_indeed("data+analyst", "California", pages=3)
    scrape_indeed("data+analyst", "New+York", pages=3)
