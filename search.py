# search.py
import sys
sys.path.insert(0, r"C:\Users\HP\Downloads\interface")

from elasticsearch import Elasticsearch

# ── Connect ───────────────────────────────────────────────────────────────────
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "norris_books"


def search_books(query, top_k=10):
    """
    Search the indexed paragraphs for a query string.
    Returns a list of matching paragraph dicts with scores.
    """
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text", "title"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"   # handles minor OCR spelling errors
                }
            },
            "size": top_k,
            "highlight": {
                "fields": {
                    "text": {
                        "fragment_size": 200,
                        "number_of_fragments": 1
                    }
                },
                "pre_tags":  ["**"],
                "post_tags": ["**"]
            }
        }
    )

    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        highlight = ""
        if "highlight" in hit and "text" in hit["highlight"]:
            highlight = hit["highlight"]["text"][0]

        results.append({
            "score":       round(hit["_score"], 3),
            "doc_id":      src["doc_id"],
            "title":       src["title"],
            "author":      src["author"],
            "year":        src["year"],
            "publisher":   src["publisher"],
            "page_number": src["page_number"],
            "para_id":     src["para_id"],
            "text":        src["text"],
            "highlight":   highlight
        })

    return results


def print_results(query, results):
    """Pretty-print search results to console."""
    print(f"\nSearch: '{query}'")
    print(f"Found {len(results)} results\n")
    print("=" * 70)

    for i, r in enumerate(results, 1):
        print(f"Result {i} — Score: {r['score']}")
        print(f"  Book:    {r['title']} ({r['year']})")
        print(f"  Author:  {r['author']}")
        print(f"  Page:    {r['page_number']}")
        print(f"  Para ID: {r['para_id']}")
        print(f"  Text:    {r['text'][:200]}...")
        if r['highlight']:
            print(f"  Match:   {r['highlight']}")
        print("-" * 70)


# ── Test when run directly ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Try a few test queries
    test_queries = [
        "grace of God",
        "nature of the soul",
        "divine light"
    ]

    for query in test_queries:
        results = search_books(query, top_k=3)
        print_results(query, results)