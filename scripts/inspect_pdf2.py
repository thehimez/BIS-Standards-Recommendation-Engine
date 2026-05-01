"""Look at structure: find pages where standards are summarized."""
import re
import fitz

PDF_PATH = "bis-rag/data/dataset.pdf"
doc = fitz.open(PDF_PATH)

# Find the first page that contains "IS 269" (the OPC 33 standard)
target = "IS 269"
for i in range(len(doc)):
    text = doc[i].get_text("text")
    if target in text:
        print(f"\n========== PAGE {i} ==========")
        print(text[:3000])
        if i < len(doc) - 1:
            nxt = doc[i+1].get_text("text")
            print(f"\n----- NEXT PAGE {i+1} -----")
            print(nxt[:1500])
        break

# find IS 8042 (white portland cement)
print("\n\n\n##### IS 8042 #####")
for i in range(len(doc)):
    text = doc[i].get_text("text")
    if "IS 8042" in text:
        print(f"\n========== PAGE {i} ==========")
        print(text[:3000])
        break

# Find some pages in the middle to understand block structure
print("\n\n\n##### PAGE 30 sample #####")
print(doc[30].get_text("text")[:3000])
print("\n\n\n##### PAGE 50 sample #####")
print(doc[50].get_text("text")[:3000])
