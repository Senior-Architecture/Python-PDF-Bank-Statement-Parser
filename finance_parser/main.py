import argparse
import os, logging
from canara_parser import canara_parser
from gpay_parser import gpay_parser

# Supperss `gray color warning`s
logging.getLogger("pdfminer").setLevel(logging.ERROR)




def parse_args():
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
    return parser.parse_args()



def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    output_path = os.path.join(args.output, f"{pdf_name}_result")

    parser_func = canara_parser if args.type == "canara" else gpay_parser
    df = parser_func(args.pdf_path)

    # Save to CSV/JSON
    if args.format == "csv":
        df.to_csv(f"{output_path}.csv", index=False, encoding="utf-8-sig")
    elif args.format == "json":
        df.to_json(f"{output_path}.json", orient="records", indent=4, force_ascii=False)
    print(f"✅ File saved to {output_path}")



if __name__ == "__main__":
    main()
