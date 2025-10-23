import camelot, re
import pandas as pd



def extract_transactions(pdf_path: str) -> list:
    """Extract structured transaction data from a Google Pay statement PDF.

    Args:
        pdf_path (str): Path to the Google Pay transaction statement PDF.

    Returns:
        list: A list of transactions, where each transaction is represented
        as a list of strings containing column-wise text data.
    """
    tables = camelot.read_pdf(pdf_path, flavor="stream", pages="all")

    transactions = []
    for table in tables:
        table = table.df

        for idx in range(1, len(table) + 1, 3):
            rows = table.iloc[idx: idx+3, :]
            transaction = []

            for col in rows.columns:
                text = ' '.join(rows[col].astype(str).str.strip().tolist())
                transaction.append(text)

            transactions.append(transaction)

    return transactions



def to_structured_df(transactions: list) -> pd.DataFrame:
    """
    Convert a raw list of Google Pay transactions into a structured pandas DataFrame.

    This function parses unstructured GPay transaction data — typically extracted from PDFs —
    and organizes it into a clean, tabular format with consistent column names and values.

    Args:
        transactions (list):
            A list of transaction entries, where each entry contains raw text segments
            (date/time, transaction details, and amount).

    Returns:
        pandas.DataFrame:
            A structured DataFrame with the following columns:
                - date (str): Transaction date formatted as DD-MM-YYYY
                - time (str): Transaction time
                - type (str): 'Credit' or 'Debit', standardized from GPay text
                - party (str): Name of the sender or receiver
                - upi_id (str): UPI transaction ID
                - account (str): Linked account or payment source
                - amount (str): Transaction amount, cleaned of currency symbols

    Processing Steps:
        1. Split the first column into date and time, and standardize date format.
        2. Use regex to extract transaction details (type, party, UPI ID, account).
        3. Normalize transaction type to 'Credit' or 'Debit'.
        4. Clean and reposition the amount column.
        5. Drop raw text columns and remove null or malformed rows.
    """

    df = pd.DataFrame(transactions)

    # first column: date and time
    df[['date', 'time']] = df[0].str.split(r'(?<=\d{4})\s+', n=1, expand=True) # Split after the year
    df['date'] = pd.to_datetime(df['date'], format='%d %b, %Y', errors='coerce').dt.strftime('%d-%m-%Y')

    # second column: transaction details
    pattern = re.compile(
        r"(?P<type>Paid\s+to|Received\s+from)\s+"                # Paid to / Received from
        r"(?P<party>[A-Za-z\s\.]+?)\s+"                          # Party name (with spaces, stop before 'UPI')
        r"UPI\s+Transaction\s+ID:\s*(?P<upi_id>[\w\d]+)\s+"      # UPI ID
        r"Paid\s+(?:to|by)\s+(?P<account>.+)$",                  # account
        re.IGNORECASE
    )

    df = df.join(df[1].str.extract(pattern))
    df["type"] = df["type"].str.replace("Paid to", "Debit", regex=False)
    df["type"] = df["type"].str.replace("Received from", "Credit", regex=False)


    # third column: Rename and reposition amount col to the last
    df.rename(columns={2: "amount"}, inplace=True)
    amt_col = df.pop('amount')
    df.insert(len(df.columns), 'amount', amt_col)
    df['amount'] = df['amount'].str.replace("₹", "")

    # Drop unwanted columns
    df.drop(columns=[0, 1], axis=1, inplace=True)

    # Drop null rows
    df.dropna(axis=0, inplace=True)

    return df



def gpay_parser(pdf_path: str) -> pd.DataFrame:
    """Parse a Google Pay transaction PDF and return a structured DataFrame.

    This function acts as a high-level wrapper that:
      1. Extracts raw transaction data from the specified GPay PDF.
      2. Converts it into a structured pandas DataFrame with standardized columns.

    Args:
        pdf_path (str):
            Path to the Google Pay transaction PDF file.

    Returns:
        pandas.DataFrame:
            A cleaned and structured DataFrame containing parsed transaction details
            such as date, time, type (Credit/Debit), party, UPI ID, account, and amount."""
    transactions = extract_transactions(pdf_path)
    return to_structured_df(transactions)
