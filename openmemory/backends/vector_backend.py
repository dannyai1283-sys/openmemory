"""Vector store backend using FAISS for semantic search"""

import os
import json
import numpy as np
from typing import List, Dict, Optional

# Try to import FAISS, fallback to simple implementation
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Using simple numpy backend.")


class VectorBackend:
    """Vector store for semantic memory search"""
    
    def __init__(self, vector_path: str, dimension: int = 384):
        self.vector_path = vector_path
        self.dimension = dimension
        self.index = None
        self.metadata = {}
        
        self._load_or_create()
    
    def _load_or_create(self):
        """Load existing index or create new"""
        index_file = os.path.join(self.vector_path, "index.faiss")
        metadata_file = os.path.join(self.vector_path, "metadata.json")
        
        if os.path.exists(index_file) and FAISS_AVAILABLE:
            self.index = faiss.read_index(index_file)
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            # Create new index
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            else:
                self.index = SimpleNumpyIndex(self.dimension)
            self.metadata = {}
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        # In production, use sentence-transformers or OpenAI embeddings
        # This is a simplified version
        try:
            from sentence_transformers import SentenceTransformer
            if not hasattr(self, '_model'):
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = self._model.encode(text)
            return embedding.astype('float32')
        except ImportError:
            # Fallback: simple hash-based embedding
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Simple fallback embedding using word hashes"""
        words = text.lower().split()
        embedding = np.zeros(self.dimension, dtype='float32')
        
        for word in words:
            # Simple hash-based encoding
            hash_val = hash(word) % self.dimension
            embedding[hash_val] += 1.0
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def add(self, memory):
        """Add memory to vector store"""
        embedding = self._get_embedding(memory.content)
        embedding = embedding.reshape(1, -1)
        
        # Add to index
        idx = self.index.ntotal if hasattr(self.index, 'ntotal') else len(self.index)
        self.index.add(embedding)
        
        # Store metadata
        self.metadata[str(idx)] = {
            "id": memory.id,
            "content": memory.content,
            "user_id": memory.user_id,
            "category": memory.category
        }
        
        self._save()
    
    def search(
        self,
        query: str,
        user_id: str = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """Search for similar memories"""
        query_embedding = self._get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search index
        if FAISS_AVAILABLE:
            scores, indices = self.index.search(query_embedding, limit * 2)  # Get extra for filtering
        else:
            scores, indices = self.index.search(query_embedding, limit * 2)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < threshold:
                continue
            
            meta = self.metadata.get(str(idx))
            if not meta:
                continue
            
            # Filter by user_id if specified
            if user_id and meta.get("user_id") != user_id:
                continue
            
            results.append({
                "id": meta["id"],
                "content": meta["content"],
                "score": float(score),
                "category": meta.get("category", "general")
            })
            
            if len(results) >= limit:
                break
        
        return results
    
    def _save(self):
        """Save index and metadata"""
        index_file = os.path.join(self.vector_path, "index.faiss")
        metadata_file = os.path.join(self.vector_path, "metadata.json")
        
        if FAISS_AVAILABLE and hasattr(self.index, 'faiss'):
            faiss.write_index(self.index, index_file)
        else:
            self.index.save(index_file)
        
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f)


class SimpleNumpyIndex:
    """Simple numpy-based index for fallback"""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = []
    
    def add(self, vectors: np.ndarray):
        self.vectors.append(vectors[0])
    
    def search(self, query: np.ndarray, k: int):
        if not self.vectors:
            return np.array([[]]), np.array([[-1] * k])
        
        # Calculate cosine similarities
        vectors = np.array(self.vectors)
        similarities = np.dot(vectors, query[0])
        
        # Get top k
        top_k = min(k, len(similarities))
        indices = np.argsort(similarities)[-top_k:][::-1]
        scores = similarities[indices]
        
        # Pad if needed
        if len(indices) < k:
            indices = np.concatenate([indices, [-1] * (k - len(indices))])
            scores = np.concatenate([scores, [0] * (k - len(scores))])
        
        return scores.reshape(1, -1), indices.reshape(1, -1)
    
    def save(self, path: str):
        np.save(path, np.array(self.vectors))
    
    @property
    def ntotal(self):
        return len(self.vectors)
