# 🧾 Finance Parser

Extract and analyze **bank or payment transaction data** from PDF statements — all in one unified CLI tool.
The **Finance Parser** reads PDFs (GPay, Canara Bank, etc.), extracts structured transaction details, and exports them to **CSV or JSON** for easy analysis or integration.


## 🚀 Features

- ⚙️ **Multi-bank support** (GPay, Canara, and extendable to others)
- 📄 **Smart PDF parsing** using Camelot / pdfplumber
- 🧩 **CLI tool** for easy automation
- 🧹 **Data normalization & cleaning**
- 📊 **Exports to CSV and JSON**
- 🔒 Works fully offline — no external APIs


## 🏗️ Project Structure

```plaintext
finance-parser/
├── src/
│   └── finance_parser/
│       ├── __init__.py
│       ├── __main__.py             # CLI entry point
│       ├── main.py                 # Core logic
│       ├── canara_parser.py        # Bank-specific parsers
|       ├── gpay_parser.py
│       └── utils/                  # Shared helpers
│
├── media/
│   └── sample_statement.pdf        # Example input
│
├── output/
│   ├── transactions.csv
│   └── transactions.json
│
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
Place your exported bank statement (e.g., GPay, Canara) inside the media/ folder.


## 🧩 Usage

### Basic Command
```bash
python -m finance_parser "media/canara_statement.pdf" -t canara -f csv
```

or, if installed as a package:
```bash
finance-parser "media/canara_statement.pdf" -t canara -f csv
```

## ⚙️ CLI Options

| Flag | Description | Example |
|------|--------------|---------|
| `-f`, `--file` | Path to PDF file | `-f media/canara_statement.pdf` |
| `-t`, `--type` | Bank/statement type (`gpay`, `canara`, etc.) | `-t canara` |
| `-o`, `--output` | Output folder | `-o output/` |
| `--format` | Output format (`csv`, `json`, or `both`) | `--format both` |
| `-p`, `--processing` | Processing mode (`raw`, `clean`, or `masked`) | `--processing clean` |

```bash
finance-parser -f media/canara_statement.pdf -t canara -f both -p masked
```

## 🧠 How It Works

1. Detects and reads statement text using Camelot or pdfplumber.
2. Chooses the correct parser based on --type.
3. Extracts structured transaction data (date, description, debit/credit, balance).
4. Applies normalization, masking, and cleaning if required.
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


## 🧼 Example Output (CSV)

| Date        | Party       | Particulars               | Deposit   | Withdrawal | Balance   |
|-------------|-------------|---------------------------|------------|-------------|------------|
| 2025-09-12  | Swiggy      | UPI/DR/Swiggy/AXIS/...    | 0.00       | 250.00      | 22,580.35  |
| 2025-09-13  | ABC Pvt Ltd | Salary from ABC Pvt Ltd   | 50,000.00  | 0.00        | 72,580.35  |

