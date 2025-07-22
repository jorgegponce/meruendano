# TO-DO

- Focus on designing and implementing all the PDF parsing plus the storage and annotation tool necessary for the model.

- Once this is complete, we can move on to the langchain orchestration. I am going to have to learn langchain

# Currently building


🛠️ What You Could Do Right Now (MVP)

Here’s a feasible Phase 1 you could prototype:

Notes + Papers Indexing
Dump all your notes (Obsidian/Markdown) + Zotero library + PDFs
Use LangChain + FAISS to embed and store them
Semantic Q&A + Retrieval
Build a chatbot that:
Answers from your own notes first
Then uses OpenAlex to find “next best papers”
Graph View
Build a D3 or Cytoscape graph of:
Your notes
Key cited papers
Semantic clusters
Open Questions Engine (optional)
Use GPT-4 to extract and cluster:
"Challenges", "future work", "limitations" from papers
Map open problems to what you already know



GIVEN THE LAST FILE, HERE ARE THE SUGGESTED ADDITIONS:

Let me know if you want to:

- Modify the chunk size for deeper context per chunk
- Add reranking logic
- Add a fallback to full-document summarization for small papers

All great ideas.


IMPORTANT: WHEN SOTING PDFS I MUSTBE ABLE TO ALSO DISTINGUISH THEN/INDEX THEM BY DOI!!!

