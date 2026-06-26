# parser.py
import os
import re

# ── Book metadata keyed by year ───────────────────────────────────────────────
BOOK_METADATA = {
    "1687": {
        "title":     "A Collection of Miscellanies",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1687
    },
    "1688": {
        "title":     "The Theory and Regulation of Love",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1688
    },
    "1689": {
        "title":     "Reason and Religion",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1689
    },
    "1690": {
        "title":     "Reflections upon the Conduct of Human Life",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1690
    },
    "1692": {
        "title":     "Two Treatises concerning the Divine Light",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1692
    },
    "1694": {
        "title":     "Spiritual Counsel or The Fathers Advice to his Children",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1694
    },
    "1699": {
        "title":     "Practical Discourses upon the Beatitudes of our Lord and Saviour Jesus Christ",
        "author":    "John Norris",
        "publisher": "Samuel Manship",
        "year":      1699
    },
}

OCR_FOLDER = r"C:\Users\HP\Downloads\interface\OCR"

def clean_text(text):
    """Clean OCR noise from text."""
    # Remove ProQuest watermark lines
    text = re.sub(r'20\d\d ProQuest LLC.*', '', text)
    text = re.sub(r'ProQuest LLC.*', '', text)
    # Remove lines that are just garbage characters (MMM... or +++... etc)
    text = re.sub(r'^[M+\-=]{5,}$', '', text, flags=re.MULTILINE)
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def get_year_from_filename(filename):
    """Extract year from filename like NORRIS_1689_0_..."""
    match = re.search(r'NORRIS_(\d{4})_', filename)
    if match:
        return match.group(1)
    return None

def parse_file(filepath, filename):
    """
    Parse one OCR text file into a list of paragraph dicts.
    Page markers look like: (118) on their own line.
    """
    year = get_year_from_filename(filename)
    if not year or year not in BOOK_METADATA:
        print(f"  Skipping {filename} — year not recognized.")
        return []

    meta = BOOK_METADATA[year]
    doc_id = f"NORRIS_{year}"

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split content into pages using (number) pattern
    # This matches lines like (118), (119) etc.
    page_pattern = re.compile(r'^\((\d+)\)\s*$', re.MULTILINE)
    parts = page_pattern.split(content)

    paragraphs = []

    # parts will be: [pre-first-page-text, page_num, page_text, page_num, page_text, ...]
    # Skip the first element (before any page marker)
    i = 1
    while i < len(parts) - 1:
        page_number = int(parts[i])
        page_text   = parts[i + 1]
        i += 2

        # Clean the page text
        page_text = clean_text(page_text)
        if not page_text:
            continue

        # Split page into paragraphs by blank lines
        raw_paras = re.split(r'\n\s*\n', page_text)

        para_count = 0
        for para in raw_paras:
            para = para.strip()
            # Skip very short paragraphs (less than 30 chars) — likely noise
            if len(para) < 30:
                continue
            # Skip lines that are just page numbers or watermarks
            if re.match(r'^[\d\s]+$', para):
                continue

            para_count += 1
            para_id = f"{doc_id}_p{page_number}_para{para_count}"

            paragraphs.append({
                "doc_id":      doc_id,
                "title":       meta["title"],
                "author":      meta["author"],
                "publisher":   meta["publisher"],
                "year":        meta["year"],
                "page_number": page_number,
                "para_id":     para_id,
                "text":        para
            })

    print(f"  {filename}: {len(paragraphs)} paragraphs extracted.")
    return paragraphs


def parse_all_books():
    """Parse all OCR files in the OCR folder and return all paragraphs."""
    all_paragraphs = []
    print(f"Looking for OCR files in: {OCR_FOLDER}\n")

    for filename in sorted(os.listdir(OCR_FOLDER)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(OCR_FOLDER, filename)
        print(f"Parsing: {filename}")
        paras = parse_file(filepath, filename)
        all_paragraphs.extend(paras)

    print(f"\nTotal paragraphs extracted: {len(all_paragraphs)}")
    return all_paragraphs


# Test when run directly
if __name__ == "__main__":
    results = parse_all_books()
    if results:
        print("\nSample paragraph:")
        print(f"  doc_id:      {results[0]['doc_id']}")
        print(f"  title:       {results[0]['title']}")
        print(f"  page_number: {results[0]['page_number']}")
        print(f"  para_id:     {results[0]['para_id']}")
        print(f"  text:        {results[0]['text'][:100]}...")
