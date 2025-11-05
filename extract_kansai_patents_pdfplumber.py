"""
pdfplumberを使用して関西電力の特許PDFからテキストを抽出
"""
import sys
import os

# pdfplumberをインストール
try:
    import pdfplumber
    print("pdfplumber is installed")
except ImportError:
    print("Installing pdfplumber...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
    import pdfplumber

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
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            print(f"Total pages: {num_pages}")
            
            # テキストを抽出
            full_text = ""
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += f"\n\n{'='*80}\n"
                    full_text += f"Page {i + 1}\n"
                    full_text += f"{'='*80}\n\n"
                    full_text += text
            
            # テキストファイルに保存
            output_file = pdf_file.replace('.pdf', '_pdfplumber.txt')
            output_path = os.path.join(output_dir, output_file)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"Extracted text saved to: {output_path}")
            
            # 最初の1000文字を表示
            if full_text:
                print(f"\nFirst 1000 characters:")
                print("-" * 80)
                print(full_text[:1000])
                print("-" * 80)
            else:
                print("Warning: No text extracted!")
            
    except Exception as e:
        print(f"Error processing {pdf_file}: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("Extraction complete!")
print(f"Output directory: {output_dir}")
print(f"{'='*80}")
