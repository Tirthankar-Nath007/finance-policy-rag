from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple, Optional
import pickle
import os

from app.rag.pdf_processor import get_all_pdfs_and_chunk
from app.config import settings


class FAISSStore:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.vectors: Optional[np.ndarray] = None
        self.chunks: List[str] = []
        self.sources: List[str] = []
    
    def build_index(self) -> None:
        chunks, sources = get_all_pdfs_and_chunk(
            settings.pdf_dir,
            settings.chunk_size,
            settings.chunk_overlap
        )
        
        if not chunks:
            raise ValueError("No chunks found from PDFs")
        
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.vectors = self.vectorizer.fit_transform(chunks).toarray()
        
        self.chunks = chunks
        self.sources = sources
        
        self.save_index()
    
    def save_index(self) -> None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(str(settings.index_path).replace(".faiss", "_vectors.pkl"), "wb") as f:
            pickle.dump({
                "vectors": self.vectors,
                "chunks": self.chunks,
                "sources": self.sources
            }, f)
        
        if self.vectorizer:
            with open(str(settings.index_path).replace(".faiss", "_vectorizer.pkl"), "wb") as f:
                pickle.dump(self.vectorizer, f)
    
    def load_index(self) -> bool:
        vectors_path = str(settings.index_path).replace(".faiss", "_vectors.pkl")
        vectorizer_path = str(settings.index_path).replace(".faiss", "_vectorizer.pkl")
        
        if not os.path.exists(vectors_path) or not os.path.exists(vectorizer_path):
            return False
        
        try:
            with open(vectors_path, "rb") as f:
                data = pickle.load(f)
                self.vectors = data["vectors"]
                self.chunks = data["chunks"]
                self.sources = data["sources"]
            
            with open(vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
            
            return True
        except Exception:
            return False
    
    def search(self, query: str, top_k: int = 5) -> Tuple[List[str], List[str], List[float]]:
        if self.vectorizer is None or self.vectors is None:
            if not self.load_index():
                raise ValueError("Index not built or loaded")
        
        query_vector = self.vectorizer.transform([query]).toarray()
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        retrieved_chunks = []
        retrieved_sources = []
        retrieved_scores = []
        
        for idx in top_indices:
            similarity = float(similarities[idx])
            if similarity >= settings.relevance_threshold:
                retrieved_chunks.append(self.chunks[idx])
                retrieved_sources.append(self.sources[idx])
                retrieved_scores.append(similarity)
        
        return retrieved_chunks, retrieved_sources, retrieved_scores


faiss_store = FAISSStore()
