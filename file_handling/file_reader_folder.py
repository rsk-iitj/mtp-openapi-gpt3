import os
from docx import Document
import base64
from io import BytesIO

def extract_text_from_file(file_path):
    # This is a simplified placeholder. You'll need to adjust this to handle different file types.
    text = ""
    try:
        # Ensure file paths are treated as raw strings or replace '\' with '\\'
        file_path = file_path.replace('\\', '\\\\')  # Replace single backslash with double
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        print(f"Failed to read {file_path}: {str(e)}")
    return text

def extract_texts_from_folder(directory):
    supported_formats = ['.txt', '.md', '.pdf', '.xls']  # Add more as needed
    texts = []
    file_names = []  # List to hold the names of files being read
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_formats):
                file_path = os.path.join(root, file)
                file_text = extract_text_from_file(file_path)
                if file_text:
                    texts.append(file_text)
                    file_names.append(file)  # Add the file name to the list
    return texts, file_names

def save_test_plan(full_test_plan):
    doc = Document()
    for section, content in full_test_plan.items():
        doc.add_heading(section, level=1)
        doc.add_paragraph(content)
    return doc

def download_link(doc, filename, text):
    # Generate download link for the document
    buffer = BytesIO()
    doc.save(buffer)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href