import logging, re
from gpay_parser import gpay_parser

# Supperss `gray color warning`s
logging.getLogger("pdfminer").setLevel(logging.ERROR)



def main():
    pdf_path = "media/gpay_statement.pdf"
    gpay_df = gpay_parser(pdf_path)
    gpay_df.to_csv(f"output/{pdf_path.split("/")[-1].replace(".pdf", "")}_result.csv", index=False, encoding="utf-8-sig")






if __name__ == "__main__":
    main()
