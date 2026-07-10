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
        raise PdfParsingError(f"Unable to parse pdf: str(e)")