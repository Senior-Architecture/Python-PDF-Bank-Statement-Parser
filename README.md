# 🧾 Finance Parser

Extract and analyze **bank or payment transaction data** from PDF statements — an all-in-one CLI tool.  
The **Finance Parser** reads PDFs (GPay, Canara Bank, etc.), extracts structured transaction details, and exports them to **CSV or JSON** for easy analysis or integration.

## 🚀 Features

- ⚙️ **Multi-bank support** (GPay, Canara, and extendable to others)
- 📄 **Smart PDF parsing** using Camelot / pdfplumber
- 🧩 **CLI tool** for easy automation
- 🧹 **Data normalization & cleaning**
- 📊 **Exports to CSV and JSON**
- 🔒 Fully offline — no external APIs required

## 🏗️ Project Structure

```plaintext
finance-parser/
├── src/
│   └── finance_parser/
│       ├── __init__.py
│       ├── __main__.py             # CLI entry point
│       ├── main.py                 # Core logic
│       ├── canara_parser.py        # Bank-specific parsers
│       ├── gpay_parser.py
│       └── utils/                  # Shared helpers
├── media/
│   └── sample_statement.pdf        # Example input
├── output/
│   ├── transactions.csv
│   └── transactions.json
├── pyproject.toml                  # Build system & CLI entry config
├── requirements.txt
└── README.md
```

## ⚙️ Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/ibnu-umer/finance-parser.git
cd finance-parser
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Add your statement PDF
Place your bank statement (e.g., GPay, Canara) inside the `media/` folder.

## 🧩 Usage

### Basic Command
```bash
python -m finance_parser --file "media/canara_statement.pdf" --type canara --format csv
```

Or, if installed as a package:
```bash
finance-parser --file "media/canara_statement.pdf" --type canara --format csv
```

## ⚙️ CLI Options

| Flag | Description | Example |
|------|--------------|---------|
| `-f`, `--file` | Path to PDF file | `--file media/canara_statement.pdf` |
| `-t`, `--type` | Bank/statement type (`gpay`, `canara`, etc.) | `--type canara` |
| `-o`, `--output` | Output folder | `--output output/` |
| `--format` | Output format (`csv`, `json`, or `both`) | `--format both` |
| `-p`, `--privacy` | Processing mode (`raw`, `clean`, or `masked`) | `--privacy clean` |

Example:
```bash
finance-parser --file media/canara_statement.pdf --type canara --format both --privacy masked
```

## 🧠 How It Works

1. Detects and reads statement text using Camelot or pdfplumber.
2. Chooses the correct parser based on `--type`.
3. Extracts structured transaction data (date, description, debit/credit, balance, etc.).
4. Applies normalization, masking, or cleaning if requested.
5. Outputs the data in CSV or JSON formats.

## 🧰 Dependencies

- camelot-py / pdfplumber – PDF parsing  
- pandas – Data manipulation  
- argparse – Command-line interface  
- re – Regex-based parsing  

Install manually if needed:
```bash
pip install camelot-py pdfplumber pandas
```

## 🧼 Output

### GPay

- `date` – Transaction date  
- `time` – Transaction time  
- `type` – Credit/Debit  
- `payee` – Counterparty / Payee name  
- `txn_id` – UPI Transaction ID  
- `account` – Account  
- `amount` – Transaction amount  

### Canara

- `date` – Transaction date  
- `time` – Transaction time  
- `txn_type` – Credit/Debit  
- `mode` – UPI, NEFT, IMPS, etc.  
- `txn_id` – Transaction ID (for UPI/IMPS)  
- `bank_code` – 4-letter bank code  
- `payee` – Counterparty / Payee name  
- `upi_id` – UPI ID if available  
- `amount` – Transaction amount  
- `balance` – Account balance after transaction  
- `cheque_no` – Cheque number if present  

## 🥧 Sensitive Fields

Some transaction fields contain sensitive information. These are handled differently depending on the output mode.

### Sensitive Fields by Source

- **Canara Bank**
  - `upi_id`
  - `txn_id`
  - `cheque_no`

- **GPay**
  - `txn_id`

### Output Modes

1. **Raw**
   - All columns are included.
   - Sensitive fields are **not masked**.

2. **Masked**
   - All columns are included.
   - Sensitive fields are **masked** (partial hiding of UPI IDs, txn IDs, cheque numbers).

3. **Clean**
   - All sensitive fields are **dropped** from the output.
   - Only non-sensitive columns remain.

This ensures privacy while maintaining flexibility for analysis.
