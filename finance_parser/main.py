import logging, re
from gpay_parser import gpay_parser
from canara_parser import canara_parser

# Supperss `gray color warning`s
logging.getLogger("pdfminer").setLevel(logging.ERROR)



def main():
    pdf_path = "media/canara_statement.pdf"

    "For Canara statements"
    canara_df = canara_parser(pdf_path)
    canara_df.to_csv(f"output/{pdf_path.split("/")[-1].replace(".pdf", "")}_result.csv", index=False, encoding="utf-8-sig")

    "For GPay statements"
    # gpay_df = gpay_parser(pdf_path)
    # gpay_df.to_csv(f"output/{pdf_path.split("/")[-1].replace(".pdf", "")}_result.csv", index=False, encoding="utf-8-sig")






if __name__ == "__main__":
    main()
