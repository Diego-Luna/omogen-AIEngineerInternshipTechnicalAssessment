import fitz

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