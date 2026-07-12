import pdfplumber
from typing import BinaryIO


class PdfPasswordRequiredError(Exception):
    """Raised when an encrypted PDF is uploaded without a password."""
    pass

class PdfIncorrectPasswordError(Exception):
    """Raised when an incorrect password is supplied."""
    pass

class PdfParsingError(Exception):
    """Raised when the PDF cannot be parsed."""
    pass

class UnsupportedBankError(Exception):
    """Raised when the uploaded bank statement is not supported"""
    pass

def extract_text_from_pdf(pdf_stream: BinaryIO, password: str | None = None):
    try:
        with pdfplumber.open(pdf_stream, password=password) as pdf:
            page_count = len(pdf.pages)
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            
            full_text = "\n".join(pages_text)

            with open("parsed_statement.txt", 'w', encoding='utf-8') as f:
                f.write(full_text)

        return {
            'page_count': page_count,
            'raw_text': full_text
        }
    
    except ValueError:
        # Raised when password is missing or incorrect
        if password:
            raise PdfIncorrectPasswordError("Incorrect password")
        raise PdfPasswordRequiredError("This PDF is password protected.")
    
    except Exception as e:
        raise PdfParsingError(f"Unable to parse pdf: {e}")
    
def detect_bank(raw_text: str) -> str:
    if "State Bank of India" in raw_text:
        return "State Bank of India"
    else:
        raise UnsupportedBankError(f"This bank is unsupported.")
    
