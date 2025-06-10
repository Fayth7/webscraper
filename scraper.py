from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

# Configuration
OUTPUT_DIR = "ohhlala_products"
CSV_PATH = os.path.join(OUTPUT_DIR, "products.csv")
BASE_URL = "https://www.ohhlala.shop/page-shop"

# Setup
options = Options()
options.add_argument("--window-size=1920,1080")
# Uncomment the next line to run in headless mode (no browser window)
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)


def debug_page_structure():
    """Debug function to understand the page structure"""
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    print("=== DEBUGGING PAGE STRUCTURE ===")
    print(f"Page title: {soup.title.text if soup.title else 'No title found'}")
    print(f"Current URL: {driver.current_url}")

    # Look for common product container patterns
    possible_selectors = [
        'div.product-list-item',
        'div.product-item',
        'div.product',
        'div[class*="product"]',
        'article.product',
        'li.product',
        '.product-card',
        '.product-tile',
        '[data-product]'
    ]

    for selector in possible_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"Found {len(elements)} elements with selector: {selector}")
            # Show first element structure
            if elements:
                print(
                    f"First element HTML (truncated): {str(elements[0])[:200]}...")

    # Look for any divs with class containing "product"
    product_divs = soup.find_all(
        'div', class_=lambda x: x and 'product' in x.lower())
    if product_divs:
        print(f"\nFound {len(product_divs)} divs with 'product' in class name")
        for i, div in enumerate(product_divs[:3]):  # Show first 3
            print(f"Product div {i+1} classes: {div.get('class')}")

    print("=== END DEBUGGING ===\n")


def scrape_products():
    """Scrape products from current page with multiple selector attempts"""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = []

    # Try multiple possible selectors for product containers
    product_selectors = [
        'div.product-list-item',
        'div.product-item',
        'div.product',
        'div[class*="product"]',
        'article.product',
        'li.product',
        '.product-card',
        '.product-tile'
    ]

    product_elements = []
    for selector in product_selectors:
        elements = soup.select(selector)
        if elements:
            print(
                f"Using selector: {selector} (found {len(elements)} products)")
            product_elements = elements
            break

    if not product_elements:
        print("No product elements found with any selector!")
        return products

    for i, product in enumerate(product_elements):
        try:
            # Try multiple selectors for product name
            name_selectors = [
                '.product-list-item__title',
                '.product-title',
                '.product-name',
                'h2', 'h3', 'h4',
                '[class*="title"]',
                '[class*="name"]'
            ]

            name = None
            for selector in name_selectors:
                element = product.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    break

            # Try multiple selectors for price
            price_selectors = [
                '.product-list-item__price',
                '.product-price',
                '.price',
                '[class*="price"]',
                '[data-price]'
            ]

            price = None
            for selector in price_selectors:
                element = product.select_one(selector)
                if element:
                    price = element.get_text(strip=True)
                    break

            # Try multiple selectors for description
            desc_selectors = [
                '.product-list-item__description',
                '.product-description',
                '.description',
                '.product-summary',
                'p'
            ]

            description = ""
            for selector in desc_selectors:
                element = product.select_one(selector)
                if element:
                    description = element.get_text(strip=True)
                    break

            # Get image URL
            img_element = product.select_one('img')
            image_url = ""
            if img_element:
                image_url = img_element.get(
                    'src', '') or img_element.get('data-src', '')

            # Only add product if we found at least a name or price
            if name or price:
                products.append({
                    'Name': name or f"Product {i+1}",
                    'Price': price or "Price not found",
                    'Description': description,
                    'Image_URL': image_url
                })
                print(f"Successfully scraped: {name or f'Product {i+1}'}")
            else:
                print(f"Skipped product {i+1} - no name or price found")

        except Exception as e:
            print(f"Error processing product {i+1}: {e}")
            continue

    return products


def save_to_csv(products):
    """Save products to CSV with proper file handling"""
    try:
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            if products:
                writer = csv.DictWriter(csvfile, fieldnames=products[0].keys())
                writer.writeheader()
                writer.writerows(products)
            else:
                # Create empty CSV with headers
                writer = csv.DictWriter(csvfile, fieldnames=[
                                        'Name', 'Price', 'Description', 'Image_URL'])
                writer.writeheader()
    except PermissionError:
        print(
            f"Error: Cannot write to {CSV_PATH}. Please close the file if it's open in another program.")
        return False
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False
    return True


def navigate_to_page(page_number):
    """Navigate to a specific page using button-based pagination"""
    try:
        print(f"Attempting to navigate to page {page_number}")

        # Wait a moment for page to be ready
        time.sleep(2)

        # Scroll to bottom to make sure pagination is visible
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # Method 1: Try to find pagination button by data-qa attribute (most reliable based on your debug output)
        try:
            button_selector = f'button[data-qa="button-{page_number}"]'
            page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
            )
            print(f"Found page {page_number} button using data-qa selector")

            # Scroll button into view
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", page_button)
            time.sleep(1)

            # Click the button
            page_button.click()
            time.sleep(3)

            print(f"Successfully navigated to page {page_number}")
            print(f"Current URL: {driver.current_url}")
            return True

        except Exception as e:
            print(f"Method 1 (data-qa) failed: {e}")

        # Method 2: Try to find button by text content within pagination
        try:
            # Find pagination container first
            pagination = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".pagination"))
            )

            # Find button with matching text within pagination
            page_button = pagination.find_element(
                By.XPATH, f".//button[normalize-space(text())='{page_number}']"
            )

            print(f"Found page {page_number} button using text content")

            # Scroll and click
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", page_button)
            time.sleep(1)
            page_button.click()
            time.sleep(3)

            print(f"Successfully navigated to page {page_number}")
            return True

        except Exception as e:
            print(f"Method 2 (text content) failed: {e}")

        # Method 3: Try generic button selector with text
        try:
            page_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     f"//button[normalize-space(text())='{page_number}' and contains(@class, 'pagination')]")
                )
            )

            print(f"Found page {page_number} button using generic selector")
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", page_button)
            time.sleep(1)
            page_button.click()
            time.sleep(3)

            print(f"Successfully navigated to page {page_number}")
            return True

        except Exception as e:
            print(f"Method 3 (generic) failed: {e}")

        print(f"Failed to navigate to page {page_number}")
        return False

    except Exception as e:
        print(f"Error navigating to page {page_number}: {e}")
        return False


def get_total_pages():
    """Determine the total number of pages by looking at pagination buttons"""
    try:
        # Wait for pagination to load
        time.sleep(2)

        # Scroll to pagination area
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        max_page = 1

        # Method 1: Look for buttons with data-qa attributes
        try:
            pagination_buttons = driver.find_elements(
                By.CSS_SELECTOR, "button[data-qa^='button-']")
            for button in pagination_buttons:
                data_qa = button.get_attribute("data-qa")
                if data_qa and data_qa.startswith("button-"):
                    page_num_str = data_qa.replace("button-", "")
                    if page_num_str.isdigit():
                        page_num = int(page_num_str)
                        max_page = max(max_page, page_num)

            if max_page > 1:
                print(
                    f"Detected maximum page number using data-qa: {max_page}")
                return max_page

        except Exception as e:
            print(f"Method 1 for page detection failed: {e}")

        # Method 2: Look for pagination buttons by class and text
        try:
            pagination_buttons = driver.find_elements(
                By.CSS_SELECTOR, ".pagination__button")
            for button in pagination_buttons:
                text = button.text.strip()
                if text.isdigit():
                    page_num = int(text)
                    max_page = max(max_page, page_num)

            if max_page > 1:
                print(
                    f"Detected maximum page number using button text: {max_page}")
                return max_page

        except Exception as e:
            print(f"Method 2 for page detection failed: {e}")

        # Method 3: Look for any buttons with numeric text
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in all_buttons:
                text = button.text.strip()
                if text.isdigit() and len(text) <= 2:  # Reasonable page number
                    page_num = int(text)
                    max_page = max(max_page, page_num)

            if max_page > 1:
                print(
                    f"Detected maximum page number using all buttons: {max_page}")
                return max_page

        except Exception as e:
            print(f"Method 3 for page detection failed: {e}")

        print(f"Could not detect pagination, defaulting to page: {max_page}")
        return max_page

    except Exception as e:
        print(f"Error detecting total pages: {e}")
        return 1  # Default to 1 page if detection fails


def main():
    try:
        print(f"Navigating to: {BASE_URL}")
        driver.get(BASE_URL)

        # Wait for page to load completely
        time.sleep(5)
        print("Page loaded, starting scraping...")

        # Debug page structure on first page
        debug_page_structure()

        # Try to detect total pages
        total_pages = get_total_pages()
        print(f"Will attempt to scrape {total_pages} pages")

        all_products = []
        successful_pages = 0

        for page_num in range(1, total_pages + 1):
            print(f"\n{'='*50}")
            print(f"SCRAPING PAGE {page_num}")
            print(f"{'='*50}")

            # For page 1, we're already there. For others, navigate
            if page_num > 1:
                if not navigate_to_page(page_num):
                    print(
                        f"Could not navigate to page {page_num}. Stopping here.")
                    break

                # Wait for new page content to load
                time.sleep(3)

            # Scroll to ensure all content is loaded
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            # Scrape current page
            page_products = scrape_products()

            if page_products:
                all_products.extend(page_products)
                successful_pages += 1
                print(
                    f"Found {len(page_products)} products on page {page_num}")
                print(f"Total products so far: {len(all_products)}")
            else:
                print(f"No products found on page {page_num}")
                # If we can't find products, maybe we've reached the end
                if page_num > 1:
                    print("No products found, might have reached the end. Stopping.")
                    break

        # Save results
        print(f"\n{'='*50}")
        print("SAVING RESULTS")
        print(f"{'='*50}")

        if save_to_csv(all_products):
            print(
                f"Successfully saved {len(all_products)} products to {CSV_PATH}")
            print(f"Successfully scraped {successful_pages} pages")
        else:
            print("Failed to save results")

        # Print summary
        if all_products:
            print(f"\nSample of scraped products:")
            for i, product in enumerate(all_products[:5]):
                print(f"{i+1}. {product['Name']} - {product['Price']}")
        else:
            print("No products were scraped!")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
