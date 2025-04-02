import os
from pypdf import PdfReader

def test_pdf_reading():
    """Test PDF reading capabilities directly"""
    try:
        pdf_path = "/app/data/promodeagro-pitch-deck.pdf"
        
        # Step 1: Basic file checks
        print(f"1. Checking file existence and permissions...")
        print(f"File exists: {os.path.exists(pdf_path)}")
        print(f"File size: {os.path.getsize(pdf_path)}")
        print(f"File permissions: {oct(os.stat(pdf_path).st_mode)[-3:]}")
        
        # Step 2: Try to open the file
        print("\n2. Attempting to open file...")
        with open(pdf_path, 'rb') as file:
            # Step 3: Try to create PDF reader
            print("\n3. Creating PDF reader...")
            reader = PdfReader(file)
            
            # Step 4: Get basic PDF info
            print("\n4. Getting PDF information...")
            print(f"Number of pages: {len(reader.pages)}")
            
            # Step 5: Try to read first page
            print("\n5. Reading first page...")
            first_page = reader.pages[0]
            text = first_page.extract_text()
            print(f"First page preview: {text[:200]}")
            
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}")
        print(f"Error message: {str(e)}")

if __name__ == "__main__":
    test_pdf_reading() 