from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_book_links_for_category(category_url, chromedriver_path):
    """Scrape book links from one Goodreads category/list URL."""
    service = Service(chromedriver_path)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)
    links = []

    try:
        driver.get(category_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/book/show/']")))

        page_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/book/show/']")

        for link in page_links:
            href = link.get_attribute("href")
            if href and "/book/show/" in href:
                absolute_href = urljoin("https://www.goodreads.com", href.strip())
                base_link = absolute_href.split("?")[0].split("#")[0]
                links.append(base_link)
    finally:
        driver.quit()

    return list(dict.fromkeys(links))


def main():
    # Scrape book links from every category/list URL in Category_links.txt.
    with open("../Category_links.txt", "r", encoding="utf-8") as input_file:
        category_links = [line.strip() for line in input_file if line.strip()]

    if not category_links:
        print("No category links found in ../Category_links.txt")
        return

    chromedriver_path = ChromeDriverManager().install()
    all_book_links = []

    max_list_workers = min(8, len(category_links))
    print(f"[*] Scraping {len(category_links)} lists with {max_list_workers} parallel workers")

    with ThreadPoolExecutor(max_workers=max_list_workers) as executor:
        future_to_url = {
            executor.submit(get_book_links_for_category, url, chromedriver_path): url
            for url in category_links
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                links = future.result()
                print(f"[+] Collected {len(links)} links from {url}")
                all_book_links.extend(links)
            except Exception as e:
                print(f"[-] Error collecting links from {url}: {e}")

    # Keep insertion order while removing duplicates.
    unique_links = list(dict.fromkeys(all_book_links))

    with open("../book_links.txt", "w", encoding="utf-8") as output_file:
        for href in unique_links:
            output_file.write(href + "\n")

    print(f"Saved {len(unique_links)} book links to ../book_links.txt")


if __name__ == "__main__":
    main()

 