# finance_parser/main.py
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Finance parser CLI")
    parser.add_argument("path", help="Path to pdf")
    parser.add_argument("-t", "--type", required=True, help="bank type (e.g. canara)")
    parser.add_argument("-f", "--format", choices=["csv","json"], default="csv")
    parser.add_argument("-p", "--privacy", choices=["masked","full"], default="masked")
    args = parser.parse_args()

    # quick sanity output — replace with your real logic
    print("OK: running finance_parser.main.main()")
    print("args:", args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
