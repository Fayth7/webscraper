import csv
import os
from typing import List, Dict
from .config import CSV_PATH, OUTPUT_DIR


def save_to_csv(products: List[Dict], csv_path: str) -> bool:
    """Save products to CSV with proper file handling"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            if products:
                writer = csv.DictWriter(csvfile, fieldnames=products[0].keys())
                writer.writeheader()
                writer.writerows(products)
            else:
                writer = csv.DictWriter(csvfile, fieldnames=[
                                        'Name', 'Price', 'Description', 'Image_URL'])
                writer.writeheader()
        return True
    except PermissionError:
        print(
            f"Error: Cannot write to {csv_path}. Please close the file if open.")
        return False
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False
