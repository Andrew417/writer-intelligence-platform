from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys
import os
import json
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.keys import Keys
try:
    from pymongo import MongoClient, UpdateOne  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    MongoClient = None
    UpdateOne = None

sys.stdout.reconfigure(encoding='utf-8')

class GoodreadsBookScraper:
    def __init__(self, chromedriver_path="chromedriver.exe", initialize_driver=True):
        """Initialize the scraper with Chrome WebDriver"""
        self.options = None
        self.service = None
        self.driver = None
        self.wait = None

        if initialize_driver:
            # Set up Chrome options for headless browsing and better performance
            self.options = Options()
            # self.options.add_argument("--headless=new")
            # self.options.add_argument("--window-size=1920,1080")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")


            self.service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
            self.wait = WebDriverWait(self.driver, 15)
        self.books_data = []
        self.reviews_data = []

    def extract_number(self, text):
        """Extract number from text like '267,409' or '123'"""
        if text == "N/A":
            return "N/A"
        match = re.search(r'[\d,]+', text)
        return match.group(0) if match else "N/A"
    
    def close_modal(self, wait_timeout=5):
        """Wait for modal to load, then close it"""
        print(f"[*] Checking for modal (timeout={wait_timeout}s)...")
        
        try:
            WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )
            print("[+] Modal detected, closing...")
            time.sleep(0.2)
            
            close_selectors = [
                "button[aria-label='Close modal']",
                "button[aria-label='Close']",
                "button.close",
                "button[class*='close']",
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", close_btn)
                        print(f"[+] Modal closed via: {selector}")
                        time.sleep(0.2)
                        return True
                except:
                    continue
            
            try:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                print("[+] Modal closed via Escape key")
                time.sleep(0.2)
                return True
            except:
                pass
            
        except TimeoutException:
            print("[!] No modal appeared")
            return False

        return False
    
    def click_more_reviews_button(self, current_reviews_count, target_reviews=150):
        """Click 'More reviews and ratings' button to load additional reviews"""
        clicks_made = 0
        
        while current_reviews_count < target_reviews:
            try:
                # Scroll down to find the button
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.2)
                
                # Find the "More reviews and ratings" button
                more_button = self.driver.find_element(
                    By.XPATH, 
                    "//span[contains(text(), 'More reviews and ratings')]/.."
                )
                
                # Check if button is visible
                if not more_button.is_displayed():
                    print(f"[!] 'More reviews and ratings' button is not visible - stopping")
                    break
                
                # Scroll to the button to make sure it's visible
                self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                time.sleep(0.1)
                
                # Click the button
                self.driver.execute_script("arguments[0].click();", more_button)
                print(f"[+] Clicked 'More reviews and ratings' button (click {clicks_made + 1})")
                clicks_made += 1

                # CRITICAL: Wait longer for new reviews to load and render in the DOM
                time.sleep(2)  # Give JavaScript time to render new elements
               
            except NoSuchElementException:
                print(f"[!] 'More reviews and ratings' button not found - no more reviews available")
                break
            except Exception as e:
                print(f"[!] Error clicking button: {e}")
                break
        
        if clicks_made == 0:
            print(f"[+] Already have enough reviews ({current_reviews_count} >= {target_reviews}), no clicks needed")
        else:
            print(f"[+] Total 'More reviews' clicks made: {clicks_made}")
        
        return clicks_made



    def extract_reviews(self, book_data: dict, book_id: str, num_reviews: int = 150, timeout: int = 10) -> dict:
        """
        Extract up to `num_reviews` reviews from the current page and append them to:
        - book_data["reviews"] (list of dicts)
        - self.reviews_data (list of flattened review records)

        Returns the updated book_data dict.
        """
        if "reviews" not in book_data or not isinstance(book_data["reviews"], list):
            book_data["reviews"] = []

        try:
            # Wait explicitly for ReviewsList to be present
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ReviewsList'))
            )

            # Wait for at least one review card
            review_cards = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ReviewsList article.ReviewCard'))
            )

            print(f"[+] Found {len(review_cards)} total review cards")
            print(f"[+] Extracting first {min(len(review_cards), num_reviews)} reviews...")

            for i, review_card in enumerate(review_cards[:num_reviews]):
                review_data = {
                    "number": len(book_data["reviews"]) + 1,
                    "reviewer": "N/A",
                    "rating": "N/A",
                    "text": "N/A",
                    "tags": []
                }

                # Extract reviewer name
                try:
                    aria_label = review_card.get_attribute("aria-label")
                    if aria_label and "Review by" in aria_label:
                        review_data["reviewer"] = aria_label.split("Review by ", 1)[-1].strip()
                except Exception:
                    pass

                # Extract review text
                try:
                    text_elem = review_card.find_element(By.CSS_SELECTOR, 'span.Formatted')
                    review_data["text"] = text_elem.text.strip() if text_elem.text else "N/A"
                except Exception:
                    pass

                # Extract review rating
                try:
                    rating_elem = review_card.find_element(By.CSS_SELECTOR, 'span[role="img"][aria-label*="out of"]')
                    review_data["rating"] = rating_elem.get_attribute("aria-label") or "N/A"
                except Exception:
                    pass

                # Extract review tags
                try:
                    tags = []
                    tag_elements = review_card.find_elements(By.CSS_SELECTOR, 'section.ReviewCard__tags span.Button__labelItem')
                    for tag in tag_elements:
                        tag_text = tag.text.strip() if tag.text else ""
                        if tag_text:
                            tags.append(tag_text)
                    review_data["tags"] = tags
                except Exception:
                    review_data["tags"] = []

                book_data["reviews"].append(review_data)

                # Create separate review record for reviews_data
                review_record = {
                    "book_id": book_id,
                    "book_title": book_data.get("title", "N/A"),
                    "review_number": review_data["number"],
                    "reviewer_name": review_data["reviewer"],
                    "review_rating": review_data["rating"],
                    "review_text": review_data["text"],
                    "review_tags": review_data["tags"],
                    "scraped_at": book_data.get("scraped_at"),
                }
                self.reviews_data.append(review_record)

                if (i + 1) % 10 == 0:
                    print(f"[+] Extracted {i + 1} reviews...")

            book_data["scraped_reviews_count"] = len(book_data["reviews"])
            print(f"[+] Total reviews extracted: {len(book_data['reviews'])}")

        except TimeoutException:
            print("[!] Timeout waiting for reviews to load")
            book_data["scraped_reviews_count"] = len(book_data["reviews"])
        except Exception as e:
            print(f"[!] Review extraction failed: {e}")
            book_data["scraped_reviews_count"] = len(book_data["reviews"])

        return book_data

    def extract_book_data(self, book_url, url_index, num_reviews=150):
        """Extract complete book data from book page"""
        print(f"\n[*] Scraping: {book_url}")
        
        try:
            # Increase timeout and add retry for page load
            self.driver.set_page_load_timeout(30)
            max_load_retries = 2
            load_attempt = 0
            
            while load_attempt < max_load_retries:
                try:
                    self.driver.get(book_url)
                    time.sleep(2)
                    break  # Success
                except TimeoutException:
                    load_attempt += 1
                    if load_attempt < max_load_retries:
                        print(f"[!] Page load timeout (attempt {load_attempt}/{max_load_retries}), retrying...")
                        time.sleep(1)
                    else:
                        raise
                except Exception as e:
                    if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                        load_attempt += 1
                        if load_attempt < max_load_retries:
                            print(f"[!] Connection timeout (attempt {load_attempt}/{max_load_retries}), retrying...")
                            time.sleep(1)
                        else:
                            raise
                    else:
                        raise
            if url_index == 0:
                self.close_modal()

            # Extract book ID from URL
            book_id = book_url.split("/book/show/")[1].split("-")[0]
            
            book_data = {
                "book_id": book_id,
                "url": book_url,
                "scraped_at": datetime.now().isoformat(),
                "title": "N/A",
                "author": "N/A",
                "rating": "N/A",
                "rating_count": "N/A",
                "review_count": "N/A",
                "description": "N/A",
                "edition": "N/A",
                "publication_info": "N/A",
                "pages_format": "N/A",
                "page_count": "N/A",
                "format_type": "N/A",
                "price": "N/A",
                "currently_reading": "N/A",
                "currently_reading_count": "N/A",
                "genres": [],
                "scraped_reviews_count": 0,
                "reviews": []
            }
            
            # ===== EXTRACT TITLE =====
            try:
                title_elem = self.driver.find_element(By.CSS_SELECTOR, 'h1[data-testid="bookTitle"]')
                title = (title_elem.text or "").strip()
                book_data["title"] = title
                print(f"[+] Title: {title}")
            except Exception as e:
                print(f"[-] Title extraction failed: {e}")
            
            # ===== EXTRACT AUTHOR =====
            try:
                author = self.driver.find_element(By.CSS_SELECTOR, 'span[class*="ContributorLink"][class*="name"]').text.strip()
                book_data["author"] = author
                print(f"[+] Author: {author}")
            except Exception as e:
                print(f"[-] Author extraction failed: {e}")
            
            # ===== EXTRACT RATING =====
            try:
                rating = self.driver.find_element(By.CSS_SELECTOR, 'div.RatingStatistics__rating').text.strip()
                book_data["rating"] = rating
                print(f"[+] Rating: {rating}")
            except Exception as e:
                print(f"[-] Rating extraction failed: {e}")
            
            # ===== EXTRACT RATING COUNT =====
            try:
                rating_count_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='ratingsCount']"))
                )
                rating_count_text = rating_count_elem.text.strip()
                book_data["rating_count"] = self.extract_number(rating_count_text)
                print(f"[+] Rating Count: {book_data['rating_count']}")
            except Exception as e:
                print(f"[-] Rating count extraction failed: {e}")
            
            # ===== EXTRACT REVIEW COUNT =====
            try:
                review_count_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='reviewsCount']"))
                )
                review_count_text = review_count_elem.text.strip()
                book_data["review_count"] = self.extract_number(review_count_text)
                print(f"[+] Review Count: {book_data['review_count']}")
            except Exception as e:
                print(f"[-] Review count extraction failed: {e}")
            
            # ===== EXTRACT DESCRIPTION =====
            try:
                description_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="description"]')
                description = (description_elem.text or "").strip()
                book_data["description"] = description
                print(f"[+] Description: {description[:100]}...")
            except Exception as e:
                print(f"[-] Description extraction failed: {e}")

            # ===== EXTRACT EDITION / PUBLICATION / PAGES-FORMAT / PRICE =====
            try:
                publication_info_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='publicationInfo']")
                publication_info = (publication_info_elem.text or "").strip()
                if publication_info:
                    book_data["publication_info"] = publication_info
                print(f"[+] Publication Info: {book_data['publication_info']}")
            except Exception as e:
                print(f"[-] Publication info extraction failed: {e}")

            try:
                pages_format_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='pagesFormat']")
                pages_format = (pages_format_elem.text or "").strip()
                if pages_format:
                    book_data["pages_format"] = pages_format

                    page_count_match = re.search(r"([\d,]+)\s+pages?", pages_format, re.IGNORECASE)
                    if page_count_match:
                        book_data["page_count"] = page_count_match.group(1).replace(",", "")

                    if "," in pages_format:
                        possible_format = pages_format.split(",", 1)[1].strip()
                        if possible_format:
                            book_data["format_type"] = possible_format
                print(f"[+] Pages/Format: {book_data['pages_format']}")
                print(f"[+] Page Count: {book_data['page_count']}")
                print(f"[+] Format Type: {book_data['format_type']}")
            except Exception as e:
                print(f"[-] Pages/format extraction failed: {e}")

            try:
                edition_selectors = [
                    "span.Button__labelItem",
                    "span.Button.labelItem",
                    "span.Button labelltem",
                ]
                edition_text = ""

                for selector in edition_selectors:
                    try:
                        edition_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for edition_elem in edition_elements:
                            candidate_text = (edition_elem.text or "").strip()
                            if not candidate_text:
                                continue

                            candidate_lower = candidate_text.lower()
                            if (
                                "jump to ratings and reviews" in candidate_lower
                                or "ratings and reviews" == candidate_lower
                                or "want to read" in candidate_lower
                                or "rate this book" in candidate_lower
                            ):
                                continue

                            edition_text = candidate_text
                            break

                        if edition_text:
                            break
                    except Exception:
                        continue

                if edition_text:
                    edition_clean = re.sub(r"\$\s*\d+(?:\.\d{2})?", "", edition_text).strip(" -|\t")
                    normalize = lambda value: re.sub(r"[^a-z0-9]+", "", (value or "").lower())

                    edition_norm = normalize(edition_clean)
                    format_norm = normalize(book_data.get("format_type", ""))

                    if edition_clean and edition_norm and edition_norm != format_norm:
                        book_data["edition"] = edition_clean

                    price_match = re.search(r"\$\s*\d+(?:\.\d{2})?", edition_text)
                    if price_match:
                        book_data["price"] = price_match.group(0).replace(" ", "")

                print(f"[+] Edition: {book_data['edition']}")
                print(f"[+] Price: {book_data['price']}")
            except Exception as e:
                print(f"[-] Edition/price extraction failed: {e}")

            # ===== EXTRACT SOCIAL SIGNALS (CURRENTLY READING) =====
            try:
                currently_reading_text = ""
                social_selectors = [
                    "[data-testid='currentlyReadingSignal']",
                    "div.SocialSignalsSection[data-testid='currentlyReadingSignal']",
                    "div[data-testid*='currentlyReading']",
                ]

                for selector in social_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = (elem.text or "").strip()
                        if text and "currently reading" in text.lower():
                            currently_reading_text = text
                            break
                    if currently_reading_text:
                        break

                if currently_reading_text:
                    book_data["currently_reading"] = currently_reading_text
                    count_match = re.search(r"([\d,]+)", currently_reading_text)
                    if count_match:
                        book_data["currently_reading_count"] = count_match.group(1).replace(",", "")

                print(f"[+] Currently Reading: {book_data['currently_reading']}")
                print(f"[+] Currently Reading Count: {book_data['currently_reading_count']}")
            except Exception as e:
                print(f"[-] Currently-reading extraction failed: {e}")

            # ===== EXTRACT GENRES =====
            try:
                genres = []
                seen_genres = set()

                genre_elements = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div[data-testid="genresList"] [class*="genreButton"]')
                    )
                )

                for genre in genre_elements:
                    text = (genre.text or "").strip()
                    if text and text.lower() != "genres" and text not in seen_genres:
                        seen_genres.add(text)
                        genres.append(text)
                
                book_data["genres"] = genres
                print(f"[+] Genres: {genres}")

            except Exception as e:
                print(f"[-] Genre extraction failed: {e}")
                book_data["genres"] = []
            
            # ===== SCROLL DOWN TO LOAD REVIEWS =====
            print("[*] Scrolling down to load reviews...")
            
            for scroll_attempt in range(15):
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(0.5)
                
                try:
                    reviews_list = self.driver.find_element(By.CSS_SELECTOR, 'div.ReviewsList')
                    review_cards = reviews_list.find_elements(By.CSS_SELECTOR, 'article.ReviewCard')
                    
                    if len(review_cards) > 0:
                        print(f"[+] Reviews loaded! Found {len(review_cards)} review cards")
                        break
                except:
                    pass
                
                if scroll_attempt == 14:
                    print("[!] Could not find reviews after scrolling")
            
            time.sleep(2)

            book_data = self.extract_reviews(book_data, book_id, num_reviews=num_reviews)
            
            # ===== CLICK "MORE REVIEWS" BUTTON TO LOAD MORE REVIEWS =====
            initial_review_cards = len(
                self.driver.find_elements(By.CSS_SELECTOR, 'div.ReviewsList article.ReviewCard')
            )
            print(f"[*] Current reviews loaded: {initial_review_cards}, Target: {num_reviews}")
            
            # Only click if we need more reviews
            while len(book_data["reviews"]) < num_reviews:
                print(f"[*] Attempting to click button and go to page with more reviews...")
                self.click_more_reviews_button(
                    current_reviews_count=initial_review_cards,
                    target_reviews=num_reviews,
                )
                 
                if self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog']"):
                    self.close_modal(wait_timeout=1)

                # Additional wait to ensure all reviews are fully rendered after clicking more reviews
                print("[*] Waiting for all reviews to fully render...")
                time.sleep(0.5)

                # Force a page scroll to trigger any lazy-loading
                for _ in range(3):
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(0.2)

                # ===== SCROLL DOWN AGAIN AFTER LOADING MORE =====
                print("[*] Scrolling down to finalize review loading...")
                for scroll_attempt in range(3):
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(0.2)
                
                time.sleep(0.2)
                
                # ===== EXTRACT REVIEWS =====
                book_data = self.extract_reviews(book_data, book_id, num_reviews=num_reviews - book_data["scraped_reviews_count"])
           
            
            # ===== PRINT RESULTS =====
            print(f"\n[+] ===== BOOK DATA =====")
            print(f"[+] Title: {book_data['title']}")
            print(f"[+] Author: {book_data['author']}")
            print(f"[+] Rating: {book_data['rating']}")
            print(f"[+] Rating Count: {book_data['rating_count']}")
            print(f"[+] Review Count: {book_data['review_count']}")
            print(f"[+] Description: {book_data['description'][:100]}...")
            print(f"[+] Edition: {book_data['edition']}")
            print(f"[+] Publication Info: {book_data['publication_info']}")
            print(f"[+] Pages/Format: {book_data['pages_format']}")
            print(f"[+] Page Count: {book_data['page_count']}")
            print(f"[+] Format Type: {book_data['format_type']}")
            print(f"[+] Price: {book_data['price']}")
            print(f"[+] Currently Reading: {book_data['currently_reading']}")
            print(f"[+] Currently Reading Count: {book_data['currently_reading_count']}")
            print(f"[+] Genres: {', '.join(book_data['genres'])}")
            print(f"[+] Reviews Scraped: {len(book_data['reviews'])}")
            
            # Show sample reviews
            for i, review in enumerate(book_data["reviews"][:3]):
                print(f"\n[+] Review {review['number']}:")
                print(f"    Reviewer: {review['reviewer']}")
                print(f"    Rating: {review['rating']}")
                text_preview = review['text'][:150] + "..." if len(review['text']) > 150 else review['text']
                print(f"    Text: {text_preview}")
            
            self.books_data.append(book_data)
            return book_data
            
        except Exception as e:
            print(f"[-] Error scraping book: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_book_to_mongodb(
        self,
        book_data,
        book_reviews,
        mongo_uri="mongodb://localhost:27017/",
        db_name="books_db",
        books_collection_name="books",
        reviews_collection_name="reviews",
        books_collection=None,
        reviews_collection=None,
        client=None,
    ):
        """Save a single scraped book and its reviews to MongoDB immediately."""
        if MongoClient is None or UpdateOne is None:
            print("[-] pymongo is not installed. Install it with: pip install pymongo")
            return

        created_client = False
        try:
            if books_collection is None or reviews_collection is None:
                client = MongoClient(mongo_uri)
                client.admin.command("ping")
                created_client = True

                database = client[db_name]
                books_collection = database[books_collection_name]
                reviews_collection = database[reviews_collection_name]

            self._ensure_mongo_indexes(books_collection, reviews_collection)

            books_result = books_collection.update_one(
                {"book_id": book_data["book_id"]},
                {"$set": book_data},
                upsert=True,
            )

            review_operations = self._build_review_upserts(book_reviews)

            if review_operations:
                reviews_result = reviews_collection.bulk_write(review_operations, ordered=False)
                print(
                    f"[+] MongoDB saved book_id={book_data['book_id']} "
                    f"(book matched={books_result.matched_count}, upserted={books_result.upserted_id is not None}, "
                    f"reviews upserted={reviews_result.upserted_count})"
                )
            else:
                print(
                    f"[+] MongoDB saved book_id={book_data['book_id']} "
                    f"(book matched={books_result.matched_count}, upserted={books_result.upserted_id is not None}, no reviews)"
                )
        except Exception as e:
            print(f"[-] Error saving single book to MongoDB: {e}")
        finally:
            if created_client and client is not None:
                client.close()

    def save_to_json(self, books_filename="goodreads_books.json", reviews_filename="goodreads_reviews.json"):
        """Save scraped data to JSON files"""
        try:
            with open(books_filename, "w", encoding="utf-8") as books_file:
                json.dump(self.books_data, books_file, indent=4, ensure_ascii=False)
            print(f"\n[+] Books data saved to {books_filename}")

            with open(reviews_filename, "w", encoding="utf-8") as reviews_file:
                json.dump(self.reviews_data, reviews_file, indent=4, ensure_ascii=False)
            print(f"[+] Reviews data saved to {reviews_filename}")

            print(f"\n[+] ===== SAVE STATISTICS =====")
            print(f"[+] Total books saved: {len(self.books_data)}")
            print(f"[+] Total reviews saved: {len(self.reviews_data)}")

        except Exception as e:
            print(f"[-] Error saving to JSON: {e}")

    def close(self):
        """Close the browser"""
        if self.driver is not None:
            self.driver.quit()
            print("\n[*] Browser closed")

    def _ensure_mongo_indexes(self, books_collection, reviews_collection):
        """Ensure MongoDB indexes exist and are resilient to legacy null review keys."""
        books_collection.create_index("book_id", unique=True)

        # Clean malformed legacy docs so index creation and upserts remain stable.
        cleanup_filter = {
            "$or": [
                {"book_id": None},
                {"review_number": None},
                {"book_id": {"$exists": False}},
                {"review_number": {"$exists": False}},
            ]
        }
        deleted = reviews_collection.delete_many(cleanup_filter).deleted_count
        if deleted:
            print(f"[!] Removed {deleted} malformed review documents (null/missing keys)")

        reviews_collection.create_index(
            [("book_id", 1), ("review_number", 1)],
            unique=True,
            name="book_id_review_number_unique_non_null",
            partialFilterExpression={
                "book_id": {"$exists": True},
                "review_number": {"$exists": True},
            },
        )

    def _build_review_upserts(self, reviews):
        """Build safe review upserts, skipping malformed review records."""
        operations = []
        skipped = 0

        for review in reviews:
            book_id = review.get("book_id")
            review_number = review.get("review_number")

            if book_id in (None, "") or review_number is None:
                skipped += 1
                continue

            operations.append(
                UpdateOne(
                    {"book_id": str(book_id), "review_number": int(review_number)},
                    {"$set": review},
                    upsert=True,
                )
            )

        if skipped:
            print(f"[!] Skipped {skipped} malformed reviews missing book_id/review_number")

        return operations


def scrape_single_book(book_link, index):
    """Scrape a single book link."""
    scraper = GoodreadsBookScraper(chromedriver_path="chromedriver.exe")
    try:
        book_data = scraper.extract_book_data(book_link, url_index=index, num_reviews=150)
        return book_data, list(scraper.reviews_data)
    finally:
        scraper.close()


def extract_book_id_from_url(book_url):
    """Extract Goodreads book_id from URL safely."""
    try:
        return book_url.split("/book/show/")[1].split("-")[0]
    except Exception:
        return None


def load_saved_book_ids(books_filename):
    """Return processed Goodreads book IDs from a checkpoint file.

    This simplified loader assumes the checkpoint file is plain text with
    one book_id per line (the current format used in this project).
    """
    if not os.path.exists(books_filename):
        return set()

    try:
        with open(books_filename, "r", encoding="utf-8") as fh:
            return {line.strip() for line in fh if line.strip()}
    except Exception as e:
        print(f"[!] Could not load checkpoint IDs from {books_filename}: {e}")
        return set()

def append_id_checkpoint(checkpoint_path, book_id):
    """Append a processed book ID to the checkpoint file."""
    if book_id in (None, ""):
        return

    folder = os.path.dirname(checkpoint_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(checkpoint_path, "a", encoding="utf-8") as file:
        file.write(f"{book_id}\n")





# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    try:
        links_file_path = "scraping/links/book_links.txt"
        checkpoint_path = "scraping/links/processed_book_ids.txt"

        if not os.path.exists(links_file_path):
            print(f"[!] Book links file not found: {links_file_path}")
            book_links = []
        else:
            with open(links_file_path, "r", encoding="utf-8") as links_file:
                book_links = [line.strip() for line in links_file if line.strip()]
            print(f"[+] Loaded {len(book_links)} book links from {links_file_path}")

        # Remove duplicates while preserving the first-seen order.
        book_links = list(dict.fromkeys(book_links))
        print(f"[+] Total unique book links collected: {len(book_links)}")

        saved_book_ids = load_saved_book_ids(checkpoint_path)
        if saved_book_ids:
            print(f"[*] Resume mode: {len(saved_book_ids)} books already processed in {checkpoint_path}")

        pending_book_links = []
        skipped_links = 0

        for link in book_links:
            link_book_id = extract_book_id_from_url(link)
            if link_book_id and str(link_book_id) in saved_book_ids:
                skipped_links += 1
                continue
            pending_book_links.append(link)

        if skipped_links:
            print(f"[+] Resume mode: skipped {skipped_links} previously scraped books")
        print(f"[+] Pending book links to scrape: {len(pending_book_links)}")

        # Save-only instance to reuse class persistence methods without opening a browser.
        scraper = GoodreadsBookScraper(initialize_driver=False)

        mongo_uri = "mongodb://localhost:27017/"
        db_name = "books_db"
        books_collection_name = "books"
        reviews_collection_name = "reviews"

        mongo_client = None
        books_collection = None
        reviews_collection = None

        if MongoClient is not None and UpdateOne is not None:
            try:
                mongo_client = MongoClient(mongo_uri)
                mongo_client.admin.command("ping")

                database = mongo_client[db_name]
                books_collection = database[books_collection_name]
                reviews_collection = database[reviews_collection_name]

                scraper._ensure_mongo_indexes(books_collection, reviews_collection)
            except Exception as e:
                print(f"[-] Could not initialize MongoDB connection: {e}")
                if mongo_client is not None:
                    mongo_client.close()
                    mongo_client = None
                books_collection = None
                reviews_collection = None

        max_workers = min(8, len(pending_book_links)) if pending_book_links else 0
        if max_workers == 0:
            print("[!] No pending book links found to scrape")
        else:
            print(f"[*] Scraping {len(pending_book_links)} books with {max_workers} parallel workers")
            successful_scrapes = 0
            failed_scrapes = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {
                    executor.submit(scrape_single_book, link, i): link
                    for i, link in enumerate(pending_book_links)
                }
                # Process results as they complete
                for future in as_completed(future_to_link):
                    link = future_to_link[future]
                    try:
                        book_data, book_reviews = future.result()
                        if book_data is not None:
                            scraper.save_book_to_mongodb(
                                book_data=book_data,
                                book_reviews=book_reviews,
                                mongo_uri=mongo_uri,
                                db_name=db_name,
                                books_collection_name=books_collection_name,
                                reviews_collection_name=reviews_collection_name,
                                books_collection=books_collection,
                                reviews_collection=reviews_collection,
                                client=mongo_client,
                            )
                            processed_book_id = str(book_data["book_id"])
                            saved_book_ids.add(processed_book_id)
                            append_id_checkpoint(checkpoint_path, processed_book_id)
                            successful_scrapes += 1
                        else:
                            failed_scrapes += 1
                    except Exception as e:
                        failed_scrapes += 1
                        print(f"[-] Error processing {link}: {type(e).__name__}: {e}")
            
            print(f"\n[+] ===== SCRAPING SUMMARY =====")
            print(f"[+] Successful: {successful_scrapes}")
            print(f"[+] Failed: {failed_scrapes}")
            print(f"[+] Total: {successful_scrapes + failed_scrapes}")

        if mongo_client is not None:
            mongo_client.close()
            print("[+] MongoDB connection closed")
        
    except Exception as e:
        print(f"[-] Fatal error: {e}")
        import traceback
        traceback.print_exc()