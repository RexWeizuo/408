import fitz  # PyMuPDF
import os

pdf_path = r"d:\study\408\【讲义】1.1 操作系统概述（4.13）（公众号：里昂408考研）.pdf"
output_dir = r"d:\study\408\操作系统概述_图片"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Open PDF
doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

# Zoom factor for better resolution
zoom = 2
mat = fitz.Matrix(zoom, zoom)

for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(matrix=mat)
    output_path = os.path.join(output_dir, f"page_{i+1:03d}.png")
    pix.save(output_path)
    print(f"Saved: {output_path}")

doc.close()
print(f"\nAll {len(doc)} pages saved to: {output_dir}")
