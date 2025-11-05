"""
関西電力の特許PDFからテキストを抽出
"""
import sys

try:
    import PyPDF2
    print("PyPDF2 is installed")
except ImportError:
    print("PyPDF2 is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

import os

# PDFファイルのパス
pdf_dir = "/Users/takeda/Documents/github/SOC/関西電力のロジック"
pdf_files = [
    "JPB 007377392-000000(関電2023年11月出願).pdf",
    "JPB 007486653-000000(関電2023年10月出願).pdf",
    "JPB 007591213-000000(デジタルグリッド).pdf"
]

output_dir = "/Users/takeda/Documents/github/SOC/関西電力のロジック/extracted_text"
os.makedirs(output_dir, exist_ok=True)

for pdf_file in pdf_files:
    pdf_path = os.path.join(pdf_dir, pdf_file)
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        continue
    
    print(f"\n{'='*80}")
    print(f"Processing: {pdf_file}")
    print(f"{'='*80}")
    
    try:
        # PDFを開く
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"Total pages: {num_pages}")
            
            # テキストを抽出
            full_text = ""
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                full_text += f"\n\n{'='*80}\n"
                full_text += f"Page {page_num + 1}\n"
                full_text += f"{'='*80}\n\n"
                full_text += text
            
            # テキストファイルに保存
            output_file = pdf_file.replace('.pdf', '.txt')
            output_path = os.path.join(output_dir, output_file)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"Extracted text saved to: {output_path}")
            
            # 最初の500文字を表示
            print(f"\nFirst 500 characters:")
            print("-" * 80)
            print(full_text[:500])
            print("-" * 80)
            
    except Exception as e:
        print(f"Error processing {pdf_file}: {str(e)}")

print(f"\n{'='*80}")
print("Extraction complete!")
print(f"Output directory: {output_dir}")
print(f"{'='*80}")
