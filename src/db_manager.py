import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_json(filepath):
    """Loads a JSON file if it exists, otherwise returns an empty list."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON from {filepath}: {e}")
        return []

def save_json(filepath, data):
    """Saves data structure as pretty JSON in the specified file path."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to save JSON to {filepath}: {e}")

def load_seed_companies():
    """Loads the list of startup candidates from data/seed_companies.json."""
    return load_json(os.path.join(DATA_DIR, "seed_companies.json"))

def load_analyzed_companies():
    """Loads the list of already analyzed startups from data/analyzed_companies.json."""
    return load_json(os.path.join(DATA_DIR, "analyzed_companies.json"))

def mark_company_analyzed(name, website, category, score):
    """Adds a new company to the database of analyzed companies."""
    filepath = os.path.join(DATA_DIR, "analyzed_companies.json")
    analyzed = load_json(filepath)
    
    # Clean and check duplication
    name_clean = name.strip()
    website_clean = website.strip()
    
    exists = any(
        item.get("name", "").strip().lower() == name_clean.lower() or 
        (website_clean and item.get("website", "").strip().lower() == website_clean.lower())
        for item in analyzed
    )
    
    if not exists:
        analyzed.append({
            "name": name_clean,
            "website": website_clean,
            "category": category.strip(),
            "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "opportunity_score": score
        })
        save_json(filepath, analyzed)
        print(f"[INFO] Marked '{name_clean}' as analyzed in database.")
    else:
        print(f"[INFO] '{name_clean}' already exists in database. No update needed.")
