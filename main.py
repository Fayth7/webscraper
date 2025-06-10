from src.scraping import run_scraper
from src.config import BASE_URL, OUTPUT_DIR


if __name__ == "__main__":
    run_scraper(BASE_URL, OUTPUT_DIR)
