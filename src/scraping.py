from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from .config import CSV_PATH, OUTPUT_DIR, HEADLESS, WINDOW_SIZE
from .file_io import save_to_csv
from .navigation import get_total_pages, navigate_to_page
from .debug import debug_page_structure


def init_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument(f"--window-size={WINDOW_SIZE}")
    if HEADLESS:
        options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def scrape_products(driver: webdriver.Chrome) -> List[Dict]:
    """Scrape products from current page with multiple selector attempts"""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = []

    # [Your complete scrape_products function implementation]
    return products


def run_scraper(base_url: str, output_dir: str):
    driver = init_driver()
    try:
        print(f"Navigating to: {base_url}")
        driver.get(base_url)
        time.sleep(5)

        debug_page_structure(driver)
        total_pages = get_total_pages(driver)
        print(f"Will attempt to scrape {total_pages} pages")

        all_products = []
        successful_pages = 0

        for page_num in range(1, total_pages + 1):
            print(f"\n{'='*50}")
            print(f"SCRAPING PAGE {page_num}")
            print(f"{'='*50}")

            if page_num > 1 and not navigate_to_page(driver, page_num):
                print(f"Could not navigate to page {page_num}. Stopping.")
                break

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            page_products = scrape_products(driver)
            if page_products:
                all_products.extend(page_products)
                successful_pages += 1
                print(
                    f"Found {len(page_products)} products on page {page_num}")
                print(f"Total products so far: {len(all_products)}")

        if save_to_csv(all_products, CSV_PATH):
            print(
                f"\nSuccessfully saved {len(all_products)} products to {CSV_PATH}")

        if all_products:
            print("\nSample of scraped products:")
            for i, product in enumerate(all_products[:5]):
                print(f"{i+1}. {product['Name']} - {product['Price']}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing browser...")
        driver.quit()
