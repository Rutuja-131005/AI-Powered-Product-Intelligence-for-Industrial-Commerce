"""
Dataset Loader and Industrial Catalog Utilities
Loads and parses industrial parts from dataset.csv using csv.DictReader.
"""

import csv
import os
import pandas as pd
from typing import List, Dict, Any, Optional

def load_dataset_csv(file_path: str = "dataset.csv") -> List[Dict[str, str]]:
    """
    Open and read the dataset using csv.DictReader.
    Each row is returned as a dictionary mapping column headers to values.
    """
    # Locate dataset.csv in root or data/ directory
    if not os.path.exists(file_path):
        alt_path = os.path.join("data", os.path.basename(file_path))
        if os.path.exists(alt_path):
            file_path = alt_path
        elif os.path.exists(os.path.join(os.path.dirname(__file__), "dataset.csv")):
            file_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
        elif os.path.exists(os.path.join(os.path.dirname(__file__), "data", "dataset.csv")):
            file_path = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")

    rows = []
    # Open and read the dataset
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        # Loop through rows (each row is a dictionary)
        for row in reader:
            rows.append(row)
            
    return rows

def generate_sample_csv(output_path: str = "data/sample_industrial_input.csv", total_rows: Optional[int] = None) -> str:
    """
    Reads rows from dataset.csv and exports them to output_path.
    If total_rows is specified, limits or loops through rows.
    """
    rows = load_dataset_csv("dataset.csv")
    if not rows:
        raise FileNotFoundError("dataset.csv not found or empty.")

    if total_rows is not None and total_rows > 0:
        if total_rows <= len(rows):
            selected_rows = rows[:total_rows]
        else:
            # Repeat to match requested total_rows
            selected_rows = [rows[i % len(rows)] for i in range(total_rows)]
    else:
        selected_rows = rows

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(selected_rows)
    df.to_csv(output_path, index=False)
    print(f"Loaded {len(selected_rows)} dataset rows from dataset.csv into {output_path}")
    return output_path

if __name__ == "__main__":
    # Test reading dataset.csv using csv.DictReader
    with open("dataset.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        # Loop through rows (each row is a dictionary)
        for row in reader:
            print(row)
