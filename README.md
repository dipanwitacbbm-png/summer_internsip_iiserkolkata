# summer_internsip_iiserkolkata
# John Norris Books — Full Text Search System

A document retrieval system for 7 historical books (1687–1699) by John Norris, 
built using Elasticsearch and Streamlit.

## What This Does
- Parses OCR-processed text files of 7 old books into searchable paragraphs
- Indexes all paragraphs into Elasticsearch for fast full-text search
- Displays matching paragraphs alongside the original PDF page images
- Provides a clean web interface for searching

## Books Included
| Year | Title |
|------|-------|
| 1687 | A Collection of Miscellanies |
| 1688 | The Theory and Regulation of Love |
| 1689 | Reason and Religion |
| 1690 | Reflections upon the Conduct of Human Life |
| 1692 | Two Treatises concerning the Divine Light |
| 1694 | Spiritual Counsel |
| 1699 | Practical Discourses upon the Beatitudes |

## System Architecture
## Requirements
- Python 3.11+
- Elasticsearch 9.4.1
- Libraries: `elasticsearch==8.17.2`, `streamlit`, `pymupdf==1.21.1`, `Pillow`

## How to Run

### Step 1 — Install dependencies
```bash
pip install elasticsearch==8.17.2 streamlit pymupdf==1.21.1 Pillow
```

### Step 2 — Start Elasticsearch
Download Elasticsearch 9.4.1 and start it:
```bash
bin\elasticsearch.bat   # Windows
```
Disable security in `config/elasticsearch.yml`:
```yaml
xpack.security.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
```

### Step 3 — Set up data folders
Create this folder structure:
### Step 4 — Index the books
```bash
python indexer.py
```

### Step 5 — Run the app
```bash
python -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1 --server.headless true
```

### Step 6 — Open in browser
Go to: `http://127.0.0.1:8502`

## How to Search
1. Type any word or phrase in the search box
2. Click **Search**
3. Results show matching paragraphs with metadata
4. The original PDF page appears on the right side

## Project Structure
| File | Purpose |
|------|---------|
| `ocr_parser.py` | Parses OCR text files into paragraphs |
| `indexer.py` | Indexes paragraphs into Elasticsearch |
| `search.py` | Search function using Elasticsearch |
| `app.py` | Streamlit web interface |

## Author
Dipanwita — Summer Internship Project, IISERKolkata
