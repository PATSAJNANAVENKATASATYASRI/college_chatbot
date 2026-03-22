import pdfplumber
from PyPDF2 import PdfReader

# ✅ Extract all text from a PDF file
def process_pdf(file_obj):
    reader = PdfReader(file_obj)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# Example usage
if __name__ == "__main__":
    # Note: This example requires a "sample.pdf" file in the same directory.
    path = "sample.pdf"
    try:
        with open(path, "rb") as f:
            extracted_text = process_pdf(f)
            print(f"Extracted text from {path}:\n{extracted_text[:500]}...")
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found. Please create a sample PDF to run this example.")
    except Exception as e:
        print(f"An error occurred: {e}")
