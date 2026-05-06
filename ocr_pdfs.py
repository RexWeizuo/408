import fitz
import os
import numpy as np
from rapidocr_onnxruntime import RapidOCR

pdf_dir = r"d:\study\408\wd练习题"
output_dir = r"d:\study\408\wd练习题_文本_OCR"
os.makedirs(output_dir, exist_ok=True)

pdf_files = [
    "27wd数据结构选择题刷题本（公众号：里昂408考研）.pdf",
    "27wd计组选择题刷题本（公众号：里昂408考研）.pdf",
    "27操作系统选择题刷题本（公众号：里昂408考研）.pdf",
    "27计网选择题刷题本（公众号：里昂408考研）.pdf",
]

# Initialize RapidOCR with Chinese support
ocr = RapidOCR()

for pdf_name in pdf_files:
    pdf_path = os.path.join(pdf_dir, pdf_name)
    base_name = pdf_name.replace("（公众号：里昂408考研）.pdf", "").replace(".pdf", "")
    output_path = os.path.join(output_dir, f"{base_name}.txt")
    
    print(f"\nProcessing: {pdf_name}")
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    
    # Zoom for better OCR
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(total_pages):
            page = doc[i]
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to numpy array for OCR
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img = img[:, :, :3]  # Remove alpha channel
            
            # OCR
            result, _ = ocr(img)
            
            f.write(f"\n{'='*80}\n")
            f.write(f"--- 第 {i+1} 页 ---\n")
            f.write(f"{'='*80}\n")
            
            if result:
                for line in result:
                    text = line[1]
                    f.write(text + "\n")
            else:
                f.write("[此页无文字内容]\n")
            
            print(f"  Page {i+1}/{total_pages} done")
    
    doc.close()
    print(f"  -> Saved to {output_path}")

print("\nAll files converted with OCR!")
