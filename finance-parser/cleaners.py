from datetime import datetime



def clean_transactions(transactions):
    """Normalize raw parsed transaction data."""
    cleaned = []
    for tx in transactions:
        cleaned.append({
            "date": _normalize_date(tx["date"]),
            "description": tx["description"].strip().title(),
            "amount": float(tx["amount"]),
            "type": tx["type"].capitalize(),
            "status": tx["status"].capitalize(),
        })
    return cleaned


def _normalize_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        return date_str  # fallback if already clean
