# indexer.py
from elasticsearch import Elasticsearch, helpers
import sys
sys.path.insert(0, r"C:\Users\HP\Downloads\interface")
from parser import parse_all_books

# ── 1. Connect ────────────────────────────────────────────────────────────────
es = Elasticsearch("http://localhost:9200")

if not es.ping():
    raise ConnectionError("Cannot connect to Elasticsearch. Is it running?")
print("Connected to Elasticsearch.")

# ── 2. Index settings ─────────────────────────────────────────────────────────
INDEX_NAME = "norris_books"

MAPPING = {
    "settings": {
        "number_of_shards":   1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "doc_id":      {"type": "keyword"},
            "title":       {"type": "text"},
            "author":      {"type": "keyword"},
            "year":        {"type": "integer"},
            "publisher":   {"type": "keyword"},
            "page_number": {"type": "integer"},
            "para_id":     {"type": "keyword"},
            "text":        {"type": "text"}
        }
    }
}

# ── 3. Create index ───────────────────────────────────────────────────────────
if es.indices.exists(index=INDEX_NAME):
    print(f"Deleting existing index '{INDEX_NAME}'...")
    es.indices.delete(index=INDEX_NAME)

print(f"Creating index '{INDEX_NAME}'...")
es.indices.create(index=INDEX_NAME, body=MAPPING)
print("Index created.")

# ── 4. Parse all books ────────────────────────────────────────────────────────
print("\nParsing OCR files...")
paragraphs = parse_all_books()
print(f"Total paragraphs to index: {len(paragraphs)}")

# ── 5. Bulk index ─────────────────────────────────────────────────────────────
def generate_actions(paragraphs):
    for para in paragraphs:
        yield {
            "_index": INDEX_NAME,
            "_id":    para["para_id"],
            "_source": para
        }

print("\nIndexing...")
success, errors = helpers.bulk(
    es,
    generate_actions(paragraphs),
    chunk_size=500,
    raise_on_error=False
)

print(f"Successfully indexed: {success} paragraphs")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors[:3]:
        print(e)
else:
    print("No errors!")

# ── 6. Verify ─────────────────────────────────────────────────────────────────
import time
time.sleep(1)
es.indices.refresh(index=INDEX_NAME)
total = es.count(index=INDEX_NAME)["count"]
print(f"\nVerification: {total} documents now in Elasticsearch.")
