import re, json
import pdfplumber
import pandas as pd
from pathlib import Path
import argparse
import logging


# Supperss `gray color warning`s
logging.getLogger("pdfminer").setLevel(logging.ERROR)


def get_parser():
    parser = argparse.ArgumentParser(description="GPay Transaction PDF Parser")
    parser.add_argument("--file", required=True, help="Path to GPay PDF file")
    parser.add_argument("--format", default="both", choices=["csv", "json", "both"], help="Export format")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    return parser, args



def extract_text(pdf_path):
    """Open and extract text from pdf"""
    with pdfplumber.open(pdf_path) as pdf:
        texts = ""
        for page in pdf.pages:
            texts += (page.extract_text_simple())
    return texts



def clean_text(raw_text):
    text = raw_text.replace('\xa0', ' ')  # replace non-breaking spaces
    text = re.sub(r'\s+', ' ', text)      # collapse multiple spaces
    text = text.replace('₹ ', '₹')        # normalize currency spacing
    text = text.strip()
    return text



def extract_transactions(cleaned_text):
    # Core regex pattern for GPay transactions
    pattern = re.compile(
        r"(\d{2}[A-Za-z]{3},\d{4})\s+"
        r"(Paidto|Receivedfrom)\s*([A-Za-z0-9\s]+?)\s*₹([\d,]+)"
        r".*?(\d{2}:\d{2}[APM]{2}).*?UPITransactionID:([\w]+)",
        re.DOTALL
    )

    transactions = []
    for match in pattern.finditer(cleaned_text):
        date, txn_type, name, amount, time, upi_id = match.groups()
        transactions.append({
            "date": date,
            "time": time,
            "type": "Debit" if txn_type == "Paidto" else "Credit",
            "name": name.strip(),
            "amount": amount.replace(",", ""),
            "upi_id": upi_id.strip()
        })

    return transactions



def save_to_csv(transactions, output_path):
    if not transactions:
        print("[warn] No transactions found!")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(transactions)
    df.to_csv(output_path)
    print(f"[INFO] CSV saved at: {output_path}")



def save_to_json(transactions, output_path):
    if not transactions:
        print("[warn] No transactions found!")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=4, ensure_ascii=False)
    print(f"[INFO] JSON saved at: {output_path}")




def main():
    _, args = get_parser()

    raw_text = extract_text(args.file)
    cleaned_text = clean_text(raw_text)
    transactions = extract_transactions(cleaned_text)

    if not transactions:
        print("[ERROR] No transactions found. Check PDF format or parser logic.")
        return

    if args.format in ("csv", "both"):
        save_to_csv(transactions, f"{args.output}/transactions.csv")

    if args.format in ("json", "both"):
        save_to_json(transactions, f"{args.output}/transactions.json")




if __name__ == "__main__":
    main()




