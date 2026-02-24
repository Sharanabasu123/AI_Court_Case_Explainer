import pytesseract
from pdf2image import convert_from_bytes

def extract_text(file):
    images = convert_from_bytes(file.read())
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text