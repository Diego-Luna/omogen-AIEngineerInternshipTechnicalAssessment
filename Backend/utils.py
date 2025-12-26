import fitz
import re

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Receives the bytes of a PDF file and returns all extracted text.
    """
    text = ""
    try:

        with fitz.open(stream=file_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    
    return text

def anonymize_text(text: str) -> str:
    """
    Basic anonymization function to remove PII (Personally Identifiable Information)
    before sending data to the LLM to prevent bias.
    """
    # Replaces emails with [EMAIL]
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', text)
    
    # Replaces phones with [PHONE]
    phone_pattern = r'\b(?:\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
    text = re.sub(phone_pattern, '[PHONE]', text)
    
    # Mask generic URLS
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
    text = re.sub(url_pattern, '[LINK]', text)

    return text