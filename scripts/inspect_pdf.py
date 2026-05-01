"""Quick inspection of dataset.pdf — extract sample pages + count IS standards."""
import re
import fitz  # PyMuPDF

PDF_PATH = "bis-rag/data/dataset.pdf"

doc = fitz.open(PDF_PATH)
print(f"Total pages: {len(doc)}")

# Print first few pages of text
for i in range(0, 10):
    page = doc[i]
    text = page.get_text("text")
    print(f"\n========== PAGE {i} ==========")
    print(text[:1500])

# Pull out all IS standard mentions across the doc
all_text = []
for i in range(len(doc)):
    all_text.append(doc[i].get_text("text"))
full = "\n".join(all_text)
print(f"\n\nTotal characters: {len(full)}")

# IS standard regex
pattern = re.compile(r"IS\s*[:#]?\s*(\d+)(?:\s*\(\s*Part\s*([IVX0-9]+)\s*\))?\s*[:\-]?\s*(\d{4})?", re.IGNORECASE)
matches = pattern.findall(full)
print(f"Total IS pattern hits: {len(matches)}")
unique = set()
for m in matches:
    num, part, year = m
    if part:
        s = f"IS {num} (Part {part})"
    else:
        s = f"IS {num}"
    if year:
        s += f": {year}"
    unique.add(s)
print(f"Unique standard strings: {len(unique)}")
for s in list(sorted(unique))[:30]:
    print(" -", s)
