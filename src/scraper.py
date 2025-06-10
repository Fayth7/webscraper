from selenium import webdriver
from bs4 import BeautifulSoup
from .pagination import PaginationHandler
from .file_handler import save_to_csv


class Scraper:
    def __init__(self, base_url, output_dir):
        self.base_url = base_url
        self.output_dir = output_dir
        self.driver = self._init_driver()

    def _init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)

    def run(self):
        try:
            self.driver.get(self.base_url)
            pagination = PaginationHandler(self.driver)

            all_products = []
            while True:
                products = self._scrape_current_page()
                all_products.extend(products)

                if not pagination.next_page():
                    break

            save_to_csv(all_products, self.output_dir)

        finally:
            self.driver.quit()

    def _scrape_current_page(self):
        # Implementation details
        pass
