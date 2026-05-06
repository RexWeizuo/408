import fitz
import os
import numpy as np
from rapidocr_onnxruntime import RapidOCR

pdf_path = r"d:\study\408\【27完整版讲义】计组讲义（3.25）.pdf"
output_path = r"d:\study\408\cs_toc_ocr.txt"

# Initialize RapidOCR with Chinese support
ocr = RapidOCR()

print(f"Processing: {os.path.basename(pdf_path)}")
doc = fitz.open(pdf_path)

# Zoom for better OCR quality
zoom = 2
mat = fitz.Matrix(zoom, zoom)

with open(output_path, 'w', encoding='utf-8') as f:
    # Extract pages 2-6 (0-indexed: 1-5)
    for i in range(1, 6):
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
        
        print(f"  Page {i+1} done")

doc.close()
print(f"\nSaved to {output_path}")
