"""
Universal Document Vectorizer

Backward compatible with pdf_vectorizer
"""

from .vectorizer import DocumentVectorizer, VectorizationProgress

# Alias for backward compatibility
PDFVectorizer = DocumentVectorizer

__all__ = ["DocumentVectorizer", "PDFVectorizer", "VectorizationProgress"]
