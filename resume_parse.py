import pytesseract
from pdf2image import convert_from_path
import re
from PIL import Image
import io
import os
import sys

# Debug function
def debug_print(message):
    print(f"DEBUG: {message}")
    sys.stdout.flush()

# Specify Tesseract path directly
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  
pytesseract.pytesseract.tesseract_cmd = tesseract_path

debug_print(f"Tesseract path set to: {tesseract_path}")

def parse_resume(pdf_path, output_path):
    debug_print(f"Starting to parse resume: {pdf_path}")
    
    # Convert PDF to images
    debug_print("Converting PDF to images")
    try:
        images = convert_from_path(pdf_path)
        debug_print(f"Converted {len(images)} pages")
    except Exception as e:
        debug_print(f"Error converting PDF to images: {str(e)}")
        raise
    
    # Extract text using Tesseract OCR
    text = ""
    debug_print("Extracting text using Tesseract OCR")
    for i, image in enumerate(images):
        debug_print(f"Processing page {i+1}")
        try:
            page_text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
            text += page_text
            debug_print(f"Extracted {len(page_text)} characters from page {i+1}")
        except Exception as e:
            debug_print(f"Error processing page {i+1}: {str(e)}")
    
    # Split the text into sections
    debug_print("Splitting text into sections")
    sections = split_into_sections(text)
    debug_print(f"Found {len(sections)} sections")
    
    # Convert sections to markdown
    debug_print("Converting sections to markdown")
    md_content = convert_to_markdown(sections)
    
    # Write the markdown content to a file
    debug_print(f"Writing markdown content to {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_content)
        debug_print("Successfully wrote markdown content")
    except Exception as e:
        debug_print(f"Error writing markdown content: {str(e)}")
        raise

def split_into_sections(text):
    # Split text into lines
    lines = text.split('\n')
    
    sections = []
    current_section = {"title": "", "content": []}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is likely a section header
        if re.match(r'^[A-Z][A-Z\s]+$', line) or line.isupper():
            if current_section["title"]:
                sections.append(current_section)
            current_section = {"title": line, "content": []}
        else:
            current_section["content"].append(line)
    
    if current_section["title"]:
        sections.append(current_section)
    
    return sections

def convert_to_markdown(sections):
    md_content = ""
    for section in sections:
        md_content += f"# {section['title']}\n\n"
        for line in section['content']:
            # Check if line might be a subsection
            if re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*:?$', line):
                md_content += f"## {line}\n\n"
            else:
                md_content += f"{line}\n"
        md_content += "\n"
    return md_content

# Usage
if __name__ == "__main__":
    debug_print("Script started")
    pdf_path = 'path/to/your/resume.pdf'  # Replace with actual path
    output_path = 'path/to/your/resume.md'  # Replace with actual path
    try:
        parse_resume(pdf_path, output_path)
        debug_print("Resume parsing completed successfully")
    except Exception as e:
        debug_print(f"An error occurred during resume parsing: {str(e)}")
    debug_print("Script finished")

    # Keep the console window open on Windows
    if sys.platform.startswith('win'):
        print("Press Enter to exit...")
        input()
