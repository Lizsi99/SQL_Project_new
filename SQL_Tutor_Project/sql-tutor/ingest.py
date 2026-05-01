"""
SQL Tutor — Ingestion Pipeline

Loads markdown files from the knowledge-base directory, splits them into
overlapping chunks, embeds them with a local HuggingFace model, and stores
them in ChromaDB.

Run once or whenever the knowledge base changes:
    python ingest.py
"""

import os
import glob
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Knowledge base
ROOT = Path(__file__).parent
KNOWLEDGE_BASE = ROOT / "knowledge-base"
DB_NAME = str(ROOT / "vector_db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

print(f"Using local HuggingFace embeddings: {EMBEDDING_MODEL}")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Chunking of parameters 

CHUNK_SIZE = 600
CHUNK_OVERLAP = 150


def fetch_documents():
    """
    Walk every sub-folder of the knowledge base and load .md files.
    Tags each document with its category (folder name) in metadata.
    """
    folders = glob.glob(str(KNOWLEDGE_BASE / "*"))
    documents = []

    for folder in sorted(folders):
        category = os.path.basename(folder)
        loader = DirectoryLoader(
            folder,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        folder_docs = loader.load()
        for doc in folder_docs:
            doc.metadata["category"] = category
            documents.append(doc)

    print(f"Loaded {len(documents)} documents from {len(folders)} categories")
    return documents


def create_chunks(documents):
    """
    Split documents into overlapping text chunks.
    RecursiveCharacterTextSplitter tries to split on paragraph/sentence
    boundaries before falling back to character splits.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def build_vectorstore(chunks):
    """
    Embed all chunks and persist to ChromaDB.
    Recreates the collection from scratch on each run so the store
    always reflects the current knowledge base.
    """
    # Delete existing collection to start fresh
    if os.path.exists(DB_NAME):
        Chroma(
            persist_directory=DB_NAME,
            embedding_function=embeddings,
        ).delete_collection()
        print("Cleared existing vector store")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_NAME,
    )

    # Report store statistics
    collection = vectorstore._collection
    count = collection.count()
    sample = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
    dimensions = len(sample)
    print(
        f"Vector store ready: {count:,} vectors × {dimensions:,} dimensions"
        f"\n  Embedding model : {EMBEDDING_MODEL}"
        f"\n  Persist path    : {DB_NAME}"
    )
    return vectorstore


if __name__ == "__main__":
    print("=== SQL Tutor — Ingestion Pipeline ===\n")
    docs = fetch_documents()
    chunks = create_chunks(docs)
    build_vectorstore(chunks)
    print("\nIngestion complete.")
