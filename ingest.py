"""
Ingest local documents into the Chroma vector store.

Usage:
    python ingest.py --docs ./your-docs-folder
    python ingest.py --docs ./file.pdf
"""
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tools.vector_search import VectorSearchTool


def load_documents(path: str) -> list:
    p = Path(path)
    if p.is_dir():
        loaders = [
            DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader),
            DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(path, glob="**/*.md",  loader_cls=TextLoader),
        ]
        docs = []
        for loader in loaders:
            try:
                docs.extend(loader.load())
            except Exception:
                pass
        return docs
    elif p.suffix == ".pdf":
        return PyPDFLoader(path).load()
    else:
        return TextLoader(path).load()


def ingest(path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    print(f"📂 Loading documents from: {path}")
    docs = load_documents(path)
    print(f"   Loaded {len(docs)} raw document(s).")

    if not docs:
        print("❌ No documents loaded. Check that your files are valid PDFs or text files.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    print(f"   Split into {len(chunks)} chunks.")

    if not chunks:
        print("❌ No chunks created. Files may be empty or unreadable.")
        return

    tool = VectorSearchTool()
    tool.add_documents(chunks)
    print(f"✅ Ingested {len(chunks)} chunks into FAISS vector store.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into Chroma")
    parser.add_argument("--docs", required=True, help="Path to docs folder or file")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    args = parser.parse_args()
    ingest(args.docs, args.chunk_size, args.chunk_overlap)
