import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("AlertChecker")

# --- File Paths ---
PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
NEW_RESULTS_FILE = DATA_DIR / "verified_categorization.json"
OLD_RESULTS_STORE = DATA_DIR / "alert_data_store.json" # Our "database" of the last known state

# --- Comparison Logic ---

def load_json_data(file_path: Path) -> List[Dict[str, Any]]:
    """Loads JSON data from a file, returns empty list on error."""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}. Returning empty list.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Basic validation: ensure it's a list of dictionaries with an 'id'
            if isinstance(data, list) and all(isinstance(item, dict) and ('id' in item or 'chunk_id' in item) for item in data):
                return data
            else:
                logger.error(f"Invalid format in {file_path}. Expected a list of objects with 'id' or 'chunk_id'.")
                return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}.")
        return []
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []

def compare_results(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> List[str]:
    """Compares old and new results, returns a list of alert messages."""
    alerts = []
    
    # Create dictionaries keyed by ID for efficient lookup
    # Handles both 'id' and 'chunk_id' keys
    old_items_dict = {item.get('id', item.get('chunk_id')): item for item in old_data if item.get('id') or item.get('chunk_id')}
    new_items_dict = {item.get('id', item.get('chunk_id')): item for item in new_data if item.get('id') or item.get('chunk_id')}
    
    # Check for changes in existing items or new items
    for item_id, new_item in new_items_dict.items():
        if item_id not in old_items_dict:
            alerts.append(f"ALERT: New document chunk detected (ID: {item_id}). Summary: {new_item.get('summary', 'N/A')[:50]}...")
        else:
            old_item = old_items_dict[item_id]
            # Compare key fields (e.g., summary and tags)
            # Using set for tags comparison ignores order changes
            old_tags = set(old_item.get('tags', []))
            new_tags = set(new_item.get('tags', []))
            
            summary_changed = old_item.get('summary') != new_item.get('summary')
            tags_changed = old_tags != new_tags
            
            if summary_changed or tags_changed:
                change_details = []
                if summary_changed: change_details.append("summary updated")
                if tags_changed: change_details.append(f"tags changed (Old: {sorted(list(old_tags))}, New: {sorted(list(new_tags))})")
                alerts.append(f"ALERT: Change detected in chunk ID {item_id} ({', '.join(change_details)}).")

    # Optional: Check for deleted items (present in old but not new)
    # for item_id in old_items_dict:
    #     if item_id not in new_items_dict:
    #         alerts.append(f"INFO: Document chunk ID {item_id} seems to have been removed.")
            
    return alerts

def update_data_store(new_data: List[Dict[str, Any]], store_path: Path):
    """Overwrites the old data store with the new data."""
    try:
        store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(store_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Updated data store: {store_path}")
    except Exception as e:
        logger.error(f"Failed to update data store {store_path}: {e}")

# --- Main Execution ---
def main():
    logger.info("🚀 Starting Alert Check...")
    
    # Load the data
    new_results = load_json_data(NEW_RESULTS_FILE)
    old_results = load_json_data(OLD_RESULTS_STORE)
    
    if not new_results:
        logger.error(f"Cannot perform check: {NEW_RESULTS_FILE} is empty or invalid.")
        return

    # Compare
    detected_alerts = compare_results(old_results, new_results)
    
    # Report Alerts (Print to console for now)
    if detected_alerts:
        logger.warning(f"🚨 {len(detected_alerts)} Alert(s) Detected! 🚨")
        for alert in detected_alerts:
            print(f"  - {alert}") # Use print for visibility
    else:
        logger.info("✅ No significant changes detected since last run.")
        
    # Update the data store for the next run
    update_data_store(new_results, OLD_RESULTS_STORE)
    
    logger.info("✅ Alert Check Complete.")

if __name__ == "__main__":
    main()