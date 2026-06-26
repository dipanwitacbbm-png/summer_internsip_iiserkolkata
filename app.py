# app.py
import sys
sys.path.insert(0, r"C:\Users\HP\Downloads\interface")

import streamlit as st
import fitz
from PIL import Image
import io
import os
from elasticsearch import Elasticsearch

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Norris Search", layout="wide")

PDF_FOLDER = r"C:\Users\HP\Downloads\interface\PDF"

PDF_MAP = {
    "NORRIS_1687": "Norris A collection of miscellanies.pdf",
    "NORRIS_1688": "Norris The_theory_and_regulation_of_love.pdf",
    "NORRIS_1689": "Norris Reason_and_religion,_or,_The_g.pdf",
    "NORRIS_1690": "Norris Reflections_upon_the_conduct_o.pdf",
    "NORRIS_1692": "Norris Two Treatises concerning the divine light.pdf",
    "NORRIS_1694": "Norris Spiritual Counsel or The Fathers Advice to his Children.pdf",
    "NORRIS_1699": "Norris Practical_discourses_upon_the_.pdf",
}

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "norris_books"

# ── Search ────────────────────────────────────────────────────────────────────
def search_books(query, top_k=5):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text", "title"],
                    "fuzziness": "AUTO"
                }
            },
            "size": top_k
        }
    )
    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        src["score"] = round(hit["_score"], 3)
        results.append(src)
    return results

# ── PDF page ──────────────────────────────────────────────────────────────────
def get_page_image(doc_id, page_number):
    pdf_file = PDF_MAP.get(doc_id)
    if not pdf_file:
        return None
    path = os.path.join(PDF_FOLDER, pdf_file)
    if not os.path.exists(path):
        return None
    try:
        doc = fitz.open(path)
        target = str(page_number)
        idx = None
        for i in range(len(doc)):
            if target in doc[i].get_text():
                idx = i
                break
        if idx is None:
            idx = min(page_number - 1, len(doc) - 1)
        pix = doc[idx].get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        doc.close()
        return img
    except:
        return None

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("John Norris Books — Full Text Search")

query = st.text_input("Search query:")
top_k = st.selectbox("Number of results", [5, 10, 20])

if st.button("Search") and query:
    results = search_books(query, top_k)
    st.write(f"Found {len(results)} results")

    for i, r in enumerate(results, 1):
        st.markdown(f"---")
        st.markdown(f"**Result {i}** — {r['title']} ({r['year']}) · Page {r['page_number']} · Score: {r['score']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Book:** {r['title']}")
            st.write(f"**Author:** {r['author']}")
            st.write(f"**Year:** {r['year']}")
            st.write(f"**Page:** {r['page_number']}")
            st.write(f"**Text:** {r['text'][:400]}")
        with col2:
            img = get_page_image(r['doc_id'], r['page_number'])
            if img:
                st.image(img)
            else:
                st.info("PDF page not available")