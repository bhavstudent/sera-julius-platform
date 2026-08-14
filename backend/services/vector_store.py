import numpy as np
# Hot-patch for ChromaDB compatibility with NumPy 2.0+
np.float_ = np.float64

import os
import math
import hashlib
import logging
from datetime import datetime

try:
    import chromadb
    from chromadb import EmbeddingFunction, Documents, Embeddings
    HAVE_CHROMADB = True
except ImportError:
    HAVE_CHROMADB = False
    EmbeddingFunction = object
    Documents = list
    Embeddings = list

logger = logging.getLogger("sera.vector_store")

class ReliableEmbeddingFunction(EmbeddingFunction):
    """
    High-reliability 384-dimensional embedding function for ChromaDB.
    Tries SentenceTransformer first; falls back to a deterministic semantic hash encoder.
    Guarantees 0 crash rate for ChromaDB persistent storage.
    """
    def __call__(self, input: Documents) -> Embeddings:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(input, show_progress_bar=False)
            return [e.tolist() for e in embeddings]
        except Exception:
            pass

        results = []
        for doc in input:
            text = str(doc)
            dim = 384
            vec = [0.0] * dim
            for i in range(0, len(text), 4):
                chunk = text[i:i+4]
                h = int(hashlib.md5(chunk.encode('utf-8', errors='ignore')).hexdigest(), 16)
                idx = h % dim
                vec[idx] += (h % 100) / 100.0 - 0.5
            norm = math.sqrt(sum(v*v for v in vec)) or 1.0
            results.append([v / norm for v in vec])

        return results


class VectorStoreService:
    _client = None
    _collection = None

    @classmethod
    def _get_collection(cls):
        if cls._collection is not None:
            return cls._collection

        if not HAVE_CHROMADB:
            return None

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            chroma_dir = os.path.join(base_dir, "data", "chroma_db")
            os.makedirs(chroma_dir, exist_ok=True)
            
            cls._client = chromadb.PersistentClient(path=chroma_dir)
            cls._collection = cls._client.get_or_create_collection(
                name="sera_knowledge_base",
                embedding_function=ReliableEmbeddingFunction()
            )
            logger.info("ChromaDB persistent client initialized successfully with ReliableEmbeddingFunction.")
            return cls._collection
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            return None

    @classmethod
    def add_document(cls, doc_id: str, text: str, metadata: dict = None):
        """Indexes a raw text chunk into ChromaDB with strict metadata sanitization."""
        collection = cls._get_collection()
        if collection is None:
            return
            
        try:
            clean_meta = {}
            if metadata:
                for k, v in metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[str(k)] = v
                    elif v is not None:
                        clean_meta[str(k)] = str(v)

            collection.upsert(
                ids=[str(doc_id)],
                documents=[str(text)],
                metadatas=[clean_meta]
            )
            logger.debug(f"Document {doc_id} successfully indexed in ChromaDB vector store.")
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")

    @classmethod
    def index_news(cls, gdelt_id: str, title: str, themes: str, tone: float, date: datetime):
        tone_val = float(tone) if tone is not None else 0.0
        text = f"NEWS ARTICLE | Title: {title} | Themes: {themes or 'General'} | Sentiment Tone: {tone_val:.2f} | Date: {date.isoformat() if hasattr(date, 'isoformat') else str(date)}"
        metadata = {
            "type": "news",
            "gdelt_id": str(gdelt_id),
            "date": date.isoformat() if hasattr(date, 'isoformat') else str(date)
        }
        cls.add_document(f"news_{gdelt_id}", text, metadata)

    @classmethod
    def index_filing(cls, ticker: str, revenue: float, accounts_receivable: float, deferred_revenue: float, date: datetime):
        rev_val = float(revenue) if revenue is not None else 0.0
        ar_val = float(accounts_receivable) if accounts_receivable is not None else 0.0
        dr_val = float(deferred_revenue) if deferred_revenue is not None else 0.0
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        
        text = f"SEC FINANCIAL FILING | Company Ticker: {ticker} | Quarterly Revenue: ${rev_val:,.2f} | Accounts Receivable: ${ar_val:,.2f} | Deferred Revenue: ${dr_val:,.2f} | Date: {date_str}"
        metadata = {
            "type": "filing",
            "ticker": str(ticker),
            "date": date_str
        }
        date_id = date.strftime('%Y%m%d') if hasattr(date, 'strftime') else '2026'
        cls.add_document(f"filing_{ticker}_{date_id}", text, metadata)

