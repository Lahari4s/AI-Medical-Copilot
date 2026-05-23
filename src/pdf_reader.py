from src.ocr_utils import extract_text_from_pdf, extract_text_from_scanned_pdf

def read_pdf(file):
    text = extract_text_from_pdf(file)

    if len(text.strip()) < 50:
        file.seek(0)
        text = extract_text_from_scanned_pdf(file)

    return text