from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DocumentChunk:
    """Standardized document chunk for vectorization."""
    content: str
    summary: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None
