import os
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


class VectorSearchTool:
    def __init__(self, persist_directory: str = "./faiss_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self._db = None

    def _get_db(self):
        if self._db is None:
            if os.path.exists(self.persist_directory):
                self._db = FAISS.load_local(
                    self.persist_directory,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
        return self._db

    def search(self, query: str, k: int = 3) -> List[Dict]:
        try:
            db = self._get_db()
            if db is None:
                return [{"content": "No documents ingested yet. Run ingest.py first.", "source": "none", "score": 0.0}]
            results = db.similarity_search_with_score(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "score": float(score),
                }
                for doc, score in results
            ]
        except Exception as e:
            return [{"content": f"Search error: {e}", "source": "error", "score": 0.0}]

    def add_documents(self, documents: list) -> None:
        if self._db is None:
            self._db = FAISS.from_documents(documents, self.embeddings)
        else:
            self._db.add_documents(documents)
        self._db.save_local(self.persist_directory)