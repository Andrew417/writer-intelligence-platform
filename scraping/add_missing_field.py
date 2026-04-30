import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from pymongo import MongoClient, UpdateOne
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# 1. Connect to MongoDB
client = MongoClient("mongodb+srv://maroamgad12345_db_user:jC4tguQKdkyopzdF@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]


# 2. Query only needed fields (book_id + url)
cursor = collection.find({}, {"_id": 0, "book_id": 1, "url": 1})


# 3. Convert cursor to usable Python list
books_to_scrape = []
for doc in cursor:
    if "book_id" in doc and "url" in doc:
        books_to_scrape.append({"book_id": doc["book_id"], "url": doc["url"]})

print(f"Total books fetched: {len(books_to_scrape)}")

MAX_WORKERS = 8


def setup_driver(chromedriver_path="../chromedriver.exe"):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


def extract_to_read_count(driver, url, timeout=12):
    driver.get(url)

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='toReadSignal']"))
        )
    except Exception:
        pass

    selectors = [
        "[data-testid='toReadSignal']",
        "div.SocialSignalsSection[data-testid='toReadSignal']",
        "div[data-testid*='toRead']",
    ]

    candidates = []
    for selector in selectors:
        for element in driver.find_elements(By.CSS_SELECTOR, selector):
            text = (element.text or "").strip()
            if text:
                candidates.append(text)

    signal_count = None
    for text in candidates:
        if "want to read" in text.lower():
            match = re.search(r"([\d,]+)", text)
            if match:
                signal_count = int(match.group(1).replace(",", ""))
            break

    return signal_count


def scrape_book(book, index, total):
    book_id = book["book_id"]
    url = book["url"]
    driver = setup_driver()

    try:
        signal_count = extract_to_read_count(driver, url)
        print(f"[{index}/{total}] book_id={book_id} | want_to_read_count={signal_count} | url={url}")
        return UpdateOne(
            {"book_id": book_id},
            {"$set": {"want_to_read_count": signal_count}},
        )
    except Exception as scrape_error:
        print(f"[{index}/{total}] book_id={book_id} | scrape failed: {scrape_error} | url={url}")
        return None
    finally:
        driver.quit()


updates = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [
        executor.submit(scrape_book, book, i, len(books_to_scrape))
        for i, book in enumerate(books_to_scrape, start=1)   
    ]

    for future in as_completed(futures):
        operation = future.result()
        if operation is not None:
            updates.append(operation)

if updates:
    result = collection.bulk_write(updates, ordered=False)
    modified = result.modified_count + result.upserted_count
    print(f"Updated books: {modified}")
else:
    print("No updates prepared.")