from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_total_pages(driver: WebDriver) -> int:
    """Determine the total number of pages by looking at pagination buttons"""
    try:
        time.sleep(2)
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

        # [Rest of your get_total_pages function...]
        return max_page

    except Exception as e:
        print(f"Error detecting total pages: {e}")
        return 1


def navigate_to_page(driver: WebDriver, page_number: int) -> bool:
    """Navigate to a specific page using button-based pagination"""
    try:
        print(f"Attempting to navigate to page {page_number}")
        time.sleep(2)
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # Method 1: Try to find pagination button by data-qa attribute
        try:
            button_selector = f'button[data-qa="button-{page_number}"]'
            page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
            )
            print(f"Found page {page_number} button using data-qa selector")
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                page_button
            )
            time.sleep(1)
            page_button.click()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Method 1 (data-qa) failed: {e}")

        # [Rest of your navigate_to_page function...]
        return False

    except Exception as e:
        print(f"Error navigating to page {page_number}: {e}")
        return False
