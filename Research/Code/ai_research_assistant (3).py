# JUPYTER NOTEBOOK: AI-Enhanced Research Assistant

# STEP 1: Setup & Installations
!pip install -q langchain faiss-cpu sentence-transformers openai PyMuPDF

# STEP 2: Imports
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyMuPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.tools import tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQAWithSourcesChain
import os, json
import networkx as nx
import matplotlib.pyplot as plt

# STEP 3: Load and Parse PDFs
pdf_dir = "papers"
pdf_paths = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

all_chunks = []
all_docs_by_file = {}
loader = PyMuPDFLoader
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

for path in pdf_paths:
    raw_docs = loader(path).load()
    chunks = splitter.split_documents(raw_docs)
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(path)
    all_chunks.extend(chunks)
    all_docs_by_file[os.path.basename(path)] = chunks

# STEP 4: Create Embeddings
model_name = "intfloat/e5-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# STEP 5: Build FAISS Vector Store
vector_db = FAISS.from_documents(all_chunks, embedding=embeddings)
vector_db.save_local("vector_index")

# STEP 6: Setup OpenAI LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
retriever = vector_db.as_retriever()

# STEP 7: Tool: Paper-level Q&A with memory + sources + structured output
last_sorted_papers = []  # to store result order for follow-ups
last_responses_json = []  # to store structured response objects for reuse/output

@tool
def answer_by_paper(query: str) -> str:
    """Answer the user's question for each individual paper and return a structured summary."""
    global last_sorted_papers, last_responses_json
    summaries = []
    ordered = []
    results_json = []
    for fname, chunks in all_docs_by_file.items():
        db = FAISS.from_documents(chunks, embedding=embeddings)
        chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, retriever=db.as_retriever())
        res = chain({"question": query})
        answer = res["answer"]
        source = res.get("sources", "")
        summaries.append(f"📄 {fname}:
{answer}
Sources: {source}")
        ordered.append(fname)
        results_json.append({"file": fname, "answer": answer, "sources": source})
    last_sorted_papers = ordered
    last_responses_json = results_json
    return "\n\n".join(summaries)

@tool
def focus_on_paper(paper_index_query: str) -> str:
    """Focus on a specific paper based on the last sort order and answer a follow-up question."""
    global last_sorted_papers
    try:
        index, subquery = paper_index_query.split(":", 1)
        index = int(index.strip()) - 1
        paper = last_sorted_papers[index]
        chunks = all_docs_by_file[paper]
        db = FAISS.from_documents(chunks, embedding=embeddings)
        chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, retriever=db.as_retriever())
        res = chain({"question": subquery.strip()})
        return f"📄 {paper}:
{res['answer']}
Sources: {res.get('sources', 'unknown')}"
    except Exception as e:
        return f"Error understanding your request. Use format: '2: your question here'. Error: {e}"

@tool
def export_last_response_json(_: str) -> str:
    """Return the most recent structured JSON response from a multi-paper query."""
    return json.dumps(last_responses_json, indent=2)

@tool
def corpus_qna(query: str) -> str:
    """Ask a general question about the entire corpus of documents."""
    chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, retriever=retriever)
    result = chain({"question": query})
    return f"Corpus-wide response:\n{result['answer']}\nSources: {result.get('sources', 'unknown')}"

# STEP 8: Initialize Agent
tools = [answer_by_paper, focus_on_paper, export_last_response_json, corpus_qna]
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

# STEP 9: Ask Natural Language Meta-Questions
response = agent_executor.run(
    "Sort the papers by whether or not they use tensor network methods."
)
print("\n>>> Agent response:\n", response)

# STEP 10: Ask Follow-up
follow_up = agent_executor.run(
    "2: What type of tensor networks were used? Provide all equations relevant to this method."
)
print("\n>>> Follow-up on paper 2:\n", follow_up)

# STEP 11: Export results as JSON
dumped = agent_executor.run("export the structured results from the last summary")
with open("summary_output.json", "w") as f:
    f.write(dumped)
print("\n>>> Saved summary_output.json")

# STEP 12: General Corpus-Wide Q&A
corpus_response = agent_executor.run("corpus_qna: What are the major themes and methods discussed across all papers?")
print("\n>>> Corpus-wide synthesis:\n", corpus_response)
