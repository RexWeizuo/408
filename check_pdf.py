import PyPDF2

pdf_path = r"d:\study\408\【27版】操作系统讲义（4.22）（公众号：里昂408考研）.pdf"

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    num_pages = len(reader.pages)
    print(f"Total pages: {num_pages}")
    
    # Check first 10 pages
    for i in range(min(10, num_pages)):
        page = reader.pages[i]
        text = page.extract_text()
        print(f"\n--- Page {i+1} ---")
        print(f"Text length: {len(text) if text else 0}")
        if text and len(text) > 0:
            print(f"First 200 chars: {text[:200]}")
        
        # Check resources
        if '/Resources' in page:
            resources = page['/Resources']
            if '/XObject' in resources:
                xobjects = resources['/XObject']
                print(f"  XObjects: {len(xobjects)}")
