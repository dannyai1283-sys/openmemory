"""Configuration for OC-Mem"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryConfig:
    """Configuration for OpenClaw Memory"""
    
    # Storage paths
    base_path: str = "~/.openclaw/ocmem"
    
    # Backend toggles
    use_short_term: bool = True
    use_long_term: bool = True
    use_vector: bool = True
    
    # Short-term (session) config
    short_term_ttl: int = 86400  # 24 hours
    
    # Long-term config
    long_term_path: Optional[str] = None
    
    # Vector store config
    vector_path: Optional[str] = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Extraction config
    auto_extract: bool = True
    auto_categorize: bool = True
    min_importance_threshold: float = 0.3
    
    def __post_init__(self):
        """Resolve paths"""
        self.base_path = os.path.expanduser(self.base_path)
        
        if self.long_term_path is None:
            self.long_term_path = os.path.join(self.base_path, "long_term.db")
        
        if self.vector_path is None:
            self.vector_path = os.path.join(self.base_path, "vectors")
        
        # Ensure directories exist
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.vector_path, exist_ok=True)
