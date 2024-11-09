import os
import base64
from docx import Document
import re
from io import BytesIO
import pandas as pd
import pdfplumber
import asyncio
import aiofiles
from PIL import Image
import pytesseract  # OCR library for extracting text from images
import openai  # OpenAI client setup

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or replace with your actual API key

CHUNK_SIZE = 1024 * 1024  # 1MB chunks for large file reading

# Function to read large files in chunks
async def read_large_file_in_chunks(file_path):
    """Reads a file in chunks asynchronously."""
    content = []
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            content.append(chunk)
    return ''.join(content)

# Function to extract text from various types of files asynchronously
async def extract_text_from_file(file_path):
    """Extracts text and images from various file types asynchronously."""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.docx':
            return await extract_text_and_images_from_docx_in_chunks(file_path)
        elif ext in ['.txt', '.md']:
            return await read_large_file_in_chunks(file_path)
        elif ext == '.pdf':
            return await extract_text_and_images_from_pdf_in_chunks(file_path)
        elif ext in ['.xls', '.xlsx']:
            return await extract_text_from_excel(file_path)
        elif ext == '.doc':
            return await handle_doc_file(file_path)
    except Exception as e:
        print(f"Failed to read {file_path}: {str(e)}")
    return None

# Function to extract text and images from a .docx file in chunks
async def extract_text_and_images_from_docx_in_chunks(file_path):
    """Extracts text and images from a .docx file in chunks."""
    doc = Document(file_path)
    text_content = []
    image_descriptions = []

    # Iteratively extract text from paragraphs to manage memory effectively
    for paragraph in doc.paragraphs:
        if paragraph.text:
            text_content.append(paragraph.text)

    # Extract images from the docx file
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_bytes = rel.target_part.blob
            # Analyze the image using OCR and CLIP
            ocr_text = analyze_image_with_ocr(image_bytes)
            clip_description = await analyze_image_with_openai(image_bytes)
            image_descriptions.append(f"OCR: {ocr_text}, CLIP: {clip_description}")

    return '\n'.join(text_content) + "\n" + "\n".join(image_descriptions)

# Function to extract text and images from PDF files in chunks
async def extract_text_and_images_from_pdf_in_chunks(file_path):
    """Extracts text and images from PDF files asynchronously in chunks."""
    text_content = []
    image_descriptions = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
            # Extract images from the page
            for image in page.images:
                try:
                    image_obj = pdfplumber.pdf.PdfImage(image)
                    image_bytes = image_obj.data
                    # Analyze the image using OCR and CLIP
                    ocr_text = analyze_image_with_ocr(image_bytes)
                    clip_description = await analyze_image_with_openai(image_bytes)
                    image_descriptions.append(f"OCR: {ocr_text}, CLIP: {clip_description}")
                except Exception as e:
                    print(f"Failed to extract image from PDF: {str(e)}")

    return "\n".join(text_content) + "\n" + "\n".join(image_descriptions)

# Function to extract text from Excel files (no change needed for large file handling)
async def extract_text_from_excel(file_path):
    """Helper function to extract text from Excel files."""
    df = pd.read_excel(file_path)
    return df.to_string(header=True, index=False)

# Function to handle .doc files asynchronously (no change needed for large file handling)
async def handle_doc_file(file_path):
    """Placeholder for handling .doc files asynchronously."""
    import textract
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: textract.process(file_path).decode('utf-8'))

# Updated function to extract text from all supported files in a directory concurrently
async def extract_texts_from_folder(directory):
    """Extracts text from all supported files in a directory asynchronously and concurrently."""
    supported_formats = ['.txt', '.md', '.pdf', '.xls', '.xlsx', '.doc', '.docx']
    tasks = []

    # Loop through all files in the given directory
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_formats):
                file_path = os.path.join(root, file)
                tasks.append(extract_text_from_file(file_path))

    # Run all tasks concurrently
    return await asyncio.gather(*tasks)

# OCR Function using Tesseract
def analyze_image_with_ocr(image_bytes):
    """Uses Tesseract OCR to extract text from an image."""
    image = Image.open(BytesIO(image_bytes))
    return pytesseract.image_to_string(image)

# Function to analyze images using OpenAI (CLIP or DALL-E)
async def analyze_image_with_openai(image_bytes):
    """Uses OpenAI API to analyze an image and return a description."""
    image = Image.open(BytesIO(image_bytes))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    try:
        response = openai.Image.create(
            prompt="Describe the content of this image",
            image=image_base64,
            n=1,
            size="512x512"
        )
        description = response['data'][0]['url']
        return description
    except openai.error.OpenAIError as e:
        print(f"Error analyzing image with OpenAI: {e}")
        return "Image description could not be generated."
