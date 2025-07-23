#!/usr/bin/env python3
"""
metadata_pipeline.py

Connect to your Zotero Web API (user or group), fetch every item in your library,
and extract:

  - Core metadata (title, authors, date, DOI, ISBN, tags)
  - Standalone Zotero notes (converted from HTML to Markdown)
  - PDF attachments (downloaded via API) and their:
      • full text
      • highlights & comments (via PyMuPDF)

Writes one JSON file per item into OUTPUT_DIR.

Requirements:
  pip install python-dotenv pyzotero pymupdf html2text

Usage:
  1. Copy env.example → .env and fill in your Zotero credentials & paths.
  2. python metadata_pipeline.py
"""

import os
import json
from io import BytesIO
from dotenv import load_dotenv
from pyzotero import zotero
import fitz          # PyMuPDF
import html2text

# ─── Load environment variables ────────────────────────────────────────────────
load_dotenv()

LIBRARY_ID        = os.environ["ZOTERO_LIBRARY_ID"]
LIBRARY_TYPE      = os.environ.get("ZOTERO_LIBRARY_TYPE", "user")  # or "group"
API_KEY           = os.environ["ZOTERO_API_KEY"]

# Local path where Zotero stores PDFs (only used if you sync attachments via cloud)
ZOTERO_STORAGE_PATH = os.environ.get("ZOTERO_STORAGE_PATH", "")

# Where to write outputs
OUTPUT_DIR        = os.environ.get("OUTPUT_DIR", "zotero_export")
PDF_DIR           = os.path.join(OUTPUT_DIR, "pdfs")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Connect to Zotero API ────────────────────────────────────────────────────
zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)

# ─── Fetch all items (incl. notes & attachments metadata) ─────────────────────
items = zot.everything(zot.items())

for item in items:
    data = item["data"]
    key  = data["key"]

    record = {
        "key":         key,
        "title":       data.get("title", ""),
        "creators":    [f"{c.get('firstName','')} {c.get('lastName','')}".strip()
                        for c in data.get("creators", []) if c.get("creatorType") == "author"],
        "date":        data.get("date", ""),
        "doi":         data.get("DOI", ""),
        "isbn":        data.get("ISBN", ""),
        "tags":        [t["tag"] for t in data.get("tags", [])],
        "notes":       [],
        "attachments": [],
        "full_text":   "",
        "annotations": []
    }

    # ─── Pull standalone Zotero notes ─────────────────────────────────────────
    for note in zot.children(itemKey=key, itemType="note"):
        html = note["data"].get("note", "")
        md   = html2text.html2text(html).strip()
        if md:
            record["notes"].append(md)

    # ─── Download & parse PDF attachments ────────────────────────────────────
    for att in zot.children(itemKey=key, itemType="attachment"):
        ad = att["data"]
        if ad.get("contentType") == "application/pdf":
            record["attachments"].append(ad.get("filename", ""))
            try:
                # download PDF bytes
                pdf_bytes = zot.file(itemKey=key, fileKey=ad["key"])
                pdf_path  = os.path.join(PDF_DIR, f"{key}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)
                record["pdf_path"] = pdf_path

                # extract text & annotations
                doc = fitz.open(stream=BytesIO(pdf_bytes), filetype="pdf")
                text, annots = "", []
                for page in doc:
                    text += page.get_text()
                    for a in page.annots() or []:
                        annots.append({
                            "page":    page.number + 1,
                            "type":    a.info.get("type", ""),
                            "content": a.get_text("text").strip()
                        })
                doc.close()
                record["full_text"]   = text
                record["annotations"] = annots
                break  # assume one PDF per item
            except Exception:
                # skip if not synced or error reading
                continue

    # ─── Write out JSON ────────────────────────────────────────────────────────
    out_file = os.path.join(OUTPUT_DIR, f"{key}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

print(f"Export complete: {len(items)} items → '{OUTPUT_DIR}'")  
