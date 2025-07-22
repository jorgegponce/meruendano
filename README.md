

## 1. Metadata-generation layer

### Trigger
- Watch `pdf_dump/` (e.g. with Python's `watchdog` or a simple cron job) for new PDFs. ==**No need to implement just yet, it can all be done manually for now.**==

### Process
1. Run GROBID to pull out header metadata (title, authors, DOI, date, refs).
2. If you got a DOI, call OpenAlex to fill in missing fields (e.g. official title, affiliations, OpenAlex ID).
3. Build a `cite-key` (e.g. `Smith2021-QuantumCoherence`) and slugify it.
4. Rename & move the PDF into `literature/pdf_attachments/Smith2021-QuantumCoherence.pdf`.
5. Generate `literature/notes` and `metadata/Smith2021-QuantumCoherence.md` containing only YAML front-matter + a link to the PDF.

```
cite_key: Smith2021—QuantumCoherence
title: "Quantum Coherence in Optical Cavities"
authors:
  - Alice Smith
  - Bob Jones
doi: "10.1021/xyz123"
openalex_id: "https://openalex.org/W1234567890"
publication_date: 2021-07-15
pdf: "../pdf attachments/Smith2021—QuantumCoherence.pdf"
```

6. Record in a tiny SQLite table (or just a JSON) which cite-keys you’ve already done, so you never duplicate work.


**At this point the user opens Obsidian, sees newly minted note stubs, and can fill in any missing YAML fields, tweak author order, add keywords, etc.**

