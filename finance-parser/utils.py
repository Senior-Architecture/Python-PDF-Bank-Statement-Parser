import os
import json
import csv



def save_csv(data, output_path):
    """Write list of dicts to CSV."""
    if not data:
        return
    keys = data[0].keys()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def save_json(data, output_path):
    """Write list of dicts to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        

def ensure_dir(path):
    """Create folder if not exists."""
    os.makedirs(path, exist_ok=True)
