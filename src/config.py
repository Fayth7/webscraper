import os

# Core settings
BASE_URL =  # "add link to scrape"
OUTPUT_DIR = "products"
CSV_PATH = os.path.join(OUTPUT_DIR, "products.csv")

# Browser options
HEADLESS = False  # Set to True for production
WINDOW_SIZE = "1920,1080"
