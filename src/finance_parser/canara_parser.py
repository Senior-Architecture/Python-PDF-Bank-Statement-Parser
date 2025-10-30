import re
import pandas as pd
import pdfplumber


SENSITIVE_FIELDS = ["cheque_no", "txn_id", "upi_id"]


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
    Parse a single raw transaction text block into structured fields.

    This function extracts key financial details from unstructured
    transaction text found in bank statements (e.g., Canara, NEFT, UPI, IMPS).

    Extracted fields:
        - date (str): Transaction date in DD-MM-YYYY format.
        - time (str | None): Transaction time (HH:MM:SS) if available.
        - txn_type (str): 'Credit' or 'Debit', based on CR/DR markers.
        - mode (str): Transaction mode (e.g., UPI, NEFT, IMPS, ATM).
        - txn_id (str | None): Transaction ID (for UPI/IMPS transactions).
        - bank_code (str | None): 4-letter bank code (e.g., HDFC, SBIN).
        - payee (str | None): Counterparty or payee name inferred from details.
        - upi_id (str | None): UPI ID if available (e.g., **john@okicici).
        - amount (str | None): Transaction amount (usually the second-last number).
        - balance (str | None): Account balance after the transaction (last number).
        - cheque_no (str | None): Cheque number if found after 'Chq:'.

    Notes:
        - Handles both UPI and non-UPI transactions.
        - Cleans and normalizes text by removing noise like slashes, DR/CR tags, and spaces.
        - Attempts to infer missing UPI IDs by fallback parsing when standard regex fails.

    Returns:
        dict: A dictionary containing all parsed transaction details.
    """
    # --- Extract date ---
    date_match = re.search(r'\b(\d{2}-\d{2}-\d{4})\b', block)
    date = date_match.group(1) if date_match else None

    # --- Extract transaction type ---
    txn_type_match = re.search(
        r'\b(UPI/DR|UPI/CR|NEFT CR|NEFT DR|SBINT|REV|SERVICE CHARGES|IMPS/CR|IMPS/DR|ATM/DR|POS/DR|INT/CR)\b',
        block
    )
    txn_type_match = txn_type_match.group(1) if txn_type_match else None
    txn_type = "Credit" if "CR" in txn_type_match else "Debit"
    mode = re.sub(r'\s|/|DR|CR', '', txn_type_match)

    # --- Particulars cleanup ---
    particulars = re.sub(
            r'\b\d{2}-\d{2}-\d{4}\b|Chq:\s*\S+|(\d{1,3}(?:,\d{3})*\.\d{2})',
            '',
            block
        ).strip()

    particulars = re.sub(r'\s+', ' ', particulars)  # normalize spaces

    # Extract data according to the txn type
    txn_id = bank_code = upi_id = None
    if "UPI" in mode:
        # --- Extract Transaction ID ---
        txn_id_match = re.search(r'\d{12}', block)
        txn_id = txn_id_match.group(0) if txn_id_match else None

        # --- Bank Code ---
        bankcode_match = re.search(r'/\s*([A-Z]{4})\s*/', block)
        bank_code = bankcode_match.group(1) if bankcode_match else None

        # --- UPI ID ---
        upi_match = re.search(r'(\*\*[A-Za-z0-9._\-]+@[A-Za-z0-9._\-]+)', block)
        upi_id = upi_match.group(1) if upi_match else None
        if not upi_id:
            upi_id = re.sub(r'[-\s]', '', particulars.split('/')[5])

        # --- Payee name ---
        payee = particulars.split("/")[3].replace("\n", "")

    elif "NEFT" in mode:
        payee = particulars.split("-")[-2]

    else:
        payee = particulars.split("Chq")[0]

    # --- Extract cheque number ---
    chq_match = re.search(r'Chq:\s*(\S+)', block)
    cheque_no = chq_match.group(1) if chq_match else None

    # --- Extract balance (always last number) ---
    balance_match = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', block)
    balance = balance_match[-1] if balance_match else None

    # --- Extract amount ---
    if len(balance_match) >= 2:
        amount = balance_match[-2]

    # --- Extract time ---
    time_match = re.search(r'\d{2}:\d{2}:\d{2}', block)
    time = time_match.group(0) if time_match else None

    return {
        "date": date,
        "time": time,
        "txn_type": txn_type,
        "mode": mode,
        "txn_id": txn_id,
        "bank_code": bank_code,
        "payee": payee,
        "upi_id": upi_id,
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
