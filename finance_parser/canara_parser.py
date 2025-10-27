import re
import pandas as pd
import pdfplumber



def clean_text(text: str) -> str:
    return re.sub(
        r'Page\s*\d+\s*Date\s+Particulars\s+Deposits\s+Withdrawals\s+Balance',
        '',
        text,
        flags=re.IGNORECASE
    )



def extract_transaction_blocks(pdf_path: str) -> list:
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)

    # Extract only the text between Opening Balance  and Closing Balance
    pattern = r'Opening Balance\s+[\d,]+\.\d+\s*(.*?)\s*Closing Balance\s+[\d,]+\.\d+'
    match = re.search(pattern, text, re.DOTALL)
    transaction_block = match.group(1).strip() if match else ""
    cleaned_transactions = clean_text(transaction_block)

    pattern = r'(Chq:\s*\S+)'
    parts = re.split(pattern, cleaned_transactions)

    # Capture the Chq: pattern in parentheses, then rejoin it into the previous chunk.
    transactions = []
    for i in range(0, len(parts) - 1, 2):
        before = parts[i].strip()
        chq = parts[i + 1].strip()
        transactions.append(f"{before} {chq}".strip())

    return transactions



def parse_transaction(block: str) -> dict:
    """
    Parse a Canara Bank transaction block into structured data.
    """

    # --- Extract date ---
    date_match = re.search(r'\b(\d{2}-\d{2}-\d{4})\b', block)
    date = date_match.group(1) if date_match else None

    # --- Extract cheque number ---
    chq_match = re.search(r'Chq:\s*(\S+)', block)
    cheque_no = chq_match.group(1) if chq_match else None

    # --- Extract balance (always last number) ---
    balance_match = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', block)
    balance = balance_match[-1] if balance_match else None

    # --- Extract deposits / withdrawals ---
    deposit, withdrawal = None, None
    if len(balance_match) >= 2:
        amount = balance_match[-2]
        # Heuristic: presence of "CR" or "NEFT/CR" → deposit
        if re.search(r'\bCR\b', block, re.IGNORECASE):
            deposit = amount
        else:
            withdrawal = amount

    # --- Extract transaction type ---
    txn_type_match = re.search(
        r'\b(UPI/DR|UPI/CR|NEFT CR|NEFT DR|IMPS/CR|IMPS/DR|ATM/DR|POS/DR|INT/CR)\b',
        block
    )
    txn_type = txn_type_match.group(1) if txn_type_match else "UNKNOWN"

    # --- Extract particulars (the messy middle) ---
    particulars = re.sub(
        r'\b\d{2}-\d{2}-\d{4}\b|Chq:\s*\S+|(\d{1,3}(?:,\d{3})*\.\d{2})',
        '',
        block
    ).strip()

    particulars = re.sub(r'\s+', ' ', particulars)  # normalize spaces

    return {
        "date": date,
        "txn_type": txn_type,
        "particulars": particulars,
        "deposit": deposit,
        "withdrawal": withdrawal,
        "balance": balance,
        "cheque_no": cheque_no,
    }






transaction_blocks = extract_transaction_blocks("media/canara_statement.pdf")
transactions = [parse_transaction(block) for block in transaction_blocks]

for b in transactions:
    print(b, end='\n')
    print("*"*40)

print("length: ", len(transactions))
