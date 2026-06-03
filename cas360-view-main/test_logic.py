# This imports just the math/parsing functions from your dashboard.py file
from dashboard import parse_pdf, process

# --- SETUP YOUR TEST DATA HERE ---
PDF_FILE_PATH = "your_statement.pdf"  # Put a sample CAS PDF in the same folder
PDF_PASSWORD = "YOUR_PASSWORD_HERE"   # Your PAN or Date of Birth
# ---------------------------------

def run_test():
    print(f"1. Reading local file: {PDF_FILE_PATH}...")
    try:
        with open(PDF_FILE_PATH, "rb") as f:
            pdf_bytes = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find the file '{PDF_FILE_PATH}'. Make sure it is in the same folder.")
        return

    print("2. Parsing PDF (this might take a few seconds)...")
    raw_data, error = parse_pdf(pdf_bytes, PDF_PASSWORD)

    if error:
        print(f"❌ Error parsing PDF: {error}")
        return
        
    print("✅ PDF Parsed Successfully!")

    print("3. Processing data through your logic...")
    portfolio = process(raw_data)

    print("\n" + "="*40)
    print("🏆 TEST RESULTS 🏆")
    print("="*40)
    print(f"Investor Name:  {portfolio['investor_name']}")
    print(f"Statement Date: {portfolio['statement_date']}")
    print(f"Total Wealth:   ₹{portfolio['total_value']:,.2f}")
    print(f"Total Invested: ₹{portfolio['total_invested']:,.2f}")
    print(f"Total Schemes:  {len(portfolio['holdings'])}")
    print("="*40)

if __name__ == "__main__":
    run_test()