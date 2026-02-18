
import pypdf
import sys

# Reconfigure stdout just in case, though we write to file
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = 'C:/Users/LENOVO/Downloads/CI 006 - V2.pdf'
output_path = 'circular_006_content.txt'

try:
    reader = pypdf.PdfReader(pdf_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, page in enumerate(reader.pages):
            f.write(f"--- PAGE {i+1} ---\n")
            text = page.extract_text()
            if text:
                f.write(text)
            f.write('\n\n')
    print(f"Successfully extracted text to {output_path}")
except Exception as e:
    print(f"Error: {e}")
