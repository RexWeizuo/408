import PyPDF2
import sys

pdf_path = r"d:\study\408\【27版】操作系统讲义（4.22）（公众号：里昂408考研）.pdf"
output_path = r"d:\study\408\os_lecture_notes.txt"

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    num_pages = len(reader.pages)
    print(f"Total pages: {num_pages}")
    
    with open(output_path, 'w', encoding='utf-8') as out:
        for i in range(num_pages):
            page = reader.pages[i]
            text = page.extract_text()
            if text:
                out.write(f"\n{'='*80}\n")
                out.write(f"--- Page {i+1} ---\n")
                out.write(f"{'='*80}\n")
                out.write(text)
            if (i+1) % 50 == 0:
                print(f"Processed {i+1}/{num_pages} pages...")
    
    print(f"Extraction complete. Output saved to {output_path}")
