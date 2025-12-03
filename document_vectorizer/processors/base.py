from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
from ..domain import DocumentChunk

class BaseProcessor(ABC):
    """Base class for document processors."""
    
    @abstractmethod
    def process(self, file_path: str, **kwargs) -> List[DocumentChunk]:
        """Process file and return list of chunks."""
        pass
