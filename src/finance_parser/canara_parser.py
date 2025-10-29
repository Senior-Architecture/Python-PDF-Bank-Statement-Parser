import re
import pandas as pd
import pdfplumber


SENSITIVE_FIELDS = {
    "particulars": 1,
    "cheque_no": 0
}


def clean_text(text: str) -> str:
    "Removes page header lines"
    return re.sub(
        r'Page\s*\d+\s*Date\s+Particulars\s+Deposits\s+Withdrawals\s+Balance',
        '',
        text,
        flags=re.IGNORECASE
    )



def extract_transaction_blocks(pdf_path: str) -> list:
    """
    Extracts individual transaction text blocks from a bank statement PDF.

    Steps:
        1. Reads all text from the PDF using pdfplumber.
        2. Extracts only the section between 'Opening Balance' and 'Closing Balance'.
        3. Cleans out page headers and noise using clean_text().
        4. Splits transactions based on 'Chq:' markers and reconstructs each block.

    Returns:
        list: A list of cleaned transaction text blocks.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)

    # Extract only the text between Opening Balance  and Closing Balance
    pattern = r'Opening Balance\s+[\d,]+\.\d+\s*(.*?)\s*Closing Balance\s+[\d,]+\.\d+'
    match = re.search(pattern, text, re.DOTALL)
    transaction_block = match.group(1).strip() if match else ""
    cleaned_transactions = clean_text(transaction_block)

    pattern = r'(Chq:\s*\d*)'
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
    Parses a single raw transaction text block and extracts structured details.

    Extracted fields:
        - date: Transaction date (DD-MM-YYYY)
        - time: Transaction time (HH:MM:SS), if present
        - txn_type: Transaction type (e.g. UPI/DR, NEFT CR, IMPS/DR)
        - party: Counterparty name inferred from UPI or NEFT details
        - particulars: Remaining descriptive text after cleanup
        - amount: Transaction amount (second-last number in the block)
        - balance: Account balance after the transaction (last number)
        - cheque_no: Cheque number if present (after 'Chq:')

    Returns:
        dict: Structured transaction data extracted from the text block.
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

    # --- Extract amount ---
    if len(balance_match) >= 2:
        amount = balance_match[-2]

    # --- Extract transaction type ---
    txn_type_match = re.search(
        r'\b(UPI/DR|UPI/CR|NEFT CR|NEFT DR|SBINT|IMPS/CR|IMPS/DR|ATM/DR|POS/DR|INT/CR)\b',
        block
    )
    txn_type = txn_type_match.group(1) if txn_type_match else "UNKNOWN"

    # --- Extract time ---
    time_match = re.search(r'\d{2}:\d{2}:\d{2}', block)
    time = time_match.group(0) if time_match else None

    # --- Extract particulars (the messy middle) ---
    particulars = re.sub(
        r'\b\d{2}-\d{2}-\d{4}\b|Chq:\s*\S+|(\d{1,3}(?:,\d{3})*\.\d{2})',
        '',
        block
    ).strip()

    particulars = re.sub(r'\s+', ' ', particulars)  # normalize spaces

    # --- Extract Party name ---
    party = None
    if txn_type.startswith("UPI"):
        party = block.split("/")[3].replace("\n", "")

    elif txn_type.startswith("NEFT"):
        party = particulars.split("-")[-2]

    return {
        "date": date,
        "time": time,
        "txn_type": txn_type,
        "party": party,
        "particulars": particulars,
        "amount": amount,
        "balance": balance,
        "cheque_no": cheque_no,
    }



def to_table(transactions: list) -> pd.DataFrame:
    """
    Converts a list of parsed transaction dictionaries into a pandas DataFrame.
    """
    return pd.DataFrame(transactions)



def canara_parser(pdf_path: str) -> pd.DataFrame:
    """
    High-level wrapper that extracts and parses all transactions
    from a Canara Bank statement PDF.

    Steps:
        1. Extracts raw transaction text blocks from the PDF.
        2. Parses each block into structured transaction data.
        3. Converts the parsed results into a pandas DataFrame.

    Returns:
        pd.DataFrame: Structured table of all parsed transactions.
    """
    transaction_blocks = extract_transaction_blocks(pdf_path)
    transactions = [parse_transaction(block) for block in transaction_blocks]
    return to_table(transactions)
