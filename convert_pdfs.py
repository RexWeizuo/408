import fitz
import os
print(f"PyMuPDF version: {fitz.__version__}")

pdf_dir = r"d:\study\408\wd练习题"
output_dir = r"d:\study\408\wd练习题_文本"
os.makedirs(output_dir, exist_ok=True)

pdf_files = [
    "27wd数据结构选择题刷题本（公众号：里昂408考研）.pdf",
    "27wd计组选择题刷题本（公众号：里昂408考研）.pdf",
    "27操作系统选择题刷题本（公众号：里昂408考研）.pdf",
    "27计网选择题刷题本（公众号：里昂408考研）.pdf",
]

for pdf_name in pdf_files:
    pdf_path = os.path.join(pdf_dir, pdf_name)
    base_name = pdf_name.replace("（公众号：里昂408考研）.pdf", "").replace(".pdf", "")
    output_path = os.path.join(output_dir, f"{base_name}.txt")
    
    print(f"Processing: {pdf_name}")
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(total_pages):
            page = doc[i]
            text = page.get_text()
            f.write(f"\n{'='*80}\n")
            f.write(f"--- 第 {i+1} 页 ---\n")
            f.write(f"{'='*80}\n")
            if text:
                f.write(text)
            else:
                f.write("[此页无文字内容，可能为图片]")
    
    doc.close()
    print(f"  -> Saved to {output_path}")

print("\nAll files converted!")
