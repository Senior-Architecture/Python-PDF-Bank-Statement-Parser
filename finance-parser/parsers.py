import pdfplumber
import re



def parse_gpay(pdf_path: str):
    """Extract raw transactions from a GPay PDF."""
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # crude regex-based extraction
            matches = re.findall(r"(\d{4}-\d{2}-\d{2})\s+(.*?)\s+(\d+)\s+(Debit|Credit)\s+(Successful)", text)
            for match in matches:
                transactions.append({
                    "date": match[0],
                    "description": match[1],
                    "amount": match[2],
                    "type": match[3],
                    "status": match[4],
                })
    return transactions



def parse_canara(pdf_path: str):
    """Extract raw transactions from a Canara Bank passbook PDF."""
    pass
