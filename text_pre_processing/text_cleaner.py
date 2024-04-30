# text_cleaner.py
import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text, flags=re.UNICODE)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = text.lower()
    text = text.strip()
    return text
