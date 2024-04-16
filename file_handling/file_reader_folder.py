import os

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
