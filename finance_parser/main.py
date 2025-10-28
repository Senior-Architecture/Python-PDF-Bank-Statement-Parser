import argparse
import os, logging
from canara_parser import canara_parser, SENSITIVE_FIELDS as CANARA_FIELDS
from gpay_parser import gpay_parser, SENSITIVE_FIELDS as GPAY_FIELDS
from utils.privacy import sanitize_transactions

# Supperss `gray color warning`s
logging.getLogger("pdfminer").setLevel(logging.ERROR)




def parse_args():
    """
    Defines and parses command-line arguments for the statement parser CLI.

    Arguments:
        - pdf_path (positional): Path to the input PDF file.
        - -t / --type: Type of statement to parse ('canara' or 'gpay'). Required.
        - -o / --output: Directory to save the parsed output file (default: ./output).
        - -f / --format: Output file format ('csv' or 'json'). Default is 'csv'.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Parse bank or GPay statements from PDF and export results as CSV or JSON."
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file."
    )
    parser.add_argument(
        "-t", "--type",
        choices=["canara", "gpay"],
        required=True,
        help="Type of statement to parse."
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Directory to save the parsed output file (default: ./output)."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output file format (default: csv)."
    )
    parser.add_argument(
        "-p", "--privacy",
        choices=["full", "masked", "anonymized"],
        default="full",
        help="Privacy level for output data. Options: full (raw), masked, anonymized."
    )
    return parser.parse_args()



def main():
    """
    Entry point for the statement parser CLI.

    This function:
      1. Parses command-line arguments.
      2. Determines which parser to use (Canara Bank or GPay).
      3. Processes the provided PDF statement.
      4. Exports the parsed transactions to CSV or JSON format.

    The output file is saved in the specified directory, with the original
    PDF name suffixed by privacy level.

    Example:
        python main.py statements/canara.pdf -t canara -f json -o output
    """
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    output_path = os.path.join(args.output, f"{pdf_name}_{args.privacy}")

    parser_func, sensitive_fields = (
        (canara_parser, CANARA_FIELDS)
        if args.type == "canara"
        else (gpay_parser, GPAY_FIELDS)
    )
    df = parser_func(args.pdf_path)
    df = sanitize_transactions(df, args.privacy, sensitive_fields)

    # Save to CSV/JSON
    if args.format == "csv":
        output_file = f"{output_path}.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
    elif args.format == "json":
        output_file = f"{output_path}.json"
        df.to_json(output_file, orient="records", indent=4, force_ascii=False)
    print(f"✅ File saved to {output_file}")



if __name__ == "__main__":
    main()
