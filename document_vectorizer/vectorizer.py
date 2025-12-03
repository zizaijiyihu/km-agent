"""
Universal Document Vectorizer

Unified service for vectorizing different document types (PDF, Excel, etc.)
Fully compatible with PDFVectorizer interface for backward compatibility.
"""

import os
import sys
from typing import Dict, List, Optional
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

# Import infrastructure
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ks_infrastructure import ks_embedding, ks_qdrant

# Import processors
from .processors.pdf_processor import PDFProcessor
from .processors.excel_processor import ExcelProcessor

class VectorizationProgress:
    """
    Progress tracking object for document vectorization.
    Compatible with PDFVectorizer's VectorizationProgress.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset progress to initial state"""
        self._data = {
            "stage": "idle",  # idle, init, parsing, processing, storing, completed, error
            "total_pages": 0,
            "current_page": 0,
            "progress_percent": 0.0,
            "message": "",
            "current_step": "",
            "error": None,
            "data": {}
        }

    def update(self, **kwargs):
        """Update progress data"""
        self._data.update(kwargs)

    def get(self):
        """Get current progress snapshot"""
        return self._data.copy()

    def get_field(self, field):
        """Get specific field value"""
        return self._data.get(field)

    @property
    def is_completed(self):
        """Check if processing is completed"""
        return self._data["stage"] == "completed"

    @property
    def is_error(self):
        """Check if there's an error"""
        return self._data["stage"] == "error"

    @property
    def is_processing(self):
        """Check if currently processing"""
        return self._data["stage"] in ["init", "parsing", "processing", "storing"]


class DocumentVectorizer:
    """
    Universal Document Vectorizer.
    
    Fully compatible with PDFVectorizer interface.
    Supports: PDF (.pdf), Excel (.xlsx, .xls)
    """

    def __init__(
        self,
        collection_name: str = "ks_knowledge_base",
        vector_size: int = 4096
    ):
        """
        Initialize DocumentVectorizer.
        
        Args:
            collection_name: Qdrant collection name (default: ks_knowledge_base for compatibility)
            vector_size: Vector dimension size
        """
        self.embedding_service = ks_embedding()
        self.qdrant_client = ks_qdrant()
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Initialize processors
        self.processors = {
            ".pdf": PDFProcessor(),
            ".xlsx": ExcelProcessor(),
            ".xls": ExcelProcessor()
        }
        
        self.progress = VectorizationProgress()
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure Qdrant collection exists, create if not."""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                print(f"✓ Collection {self.collection_name} already exists, using it")
                return

            # Create collection with dual named vectors (summary + content)
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "summary_vector": VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    ),
                    "content_vector": VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                }
            )
            print(f"✓ Created collection with dual vectors: {self.collection_name}")
        except Exception as e:
            raise Exception(f"Failed to ensure collection: {e}")

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text."""
        if not text or not isinstance(text, str):
            text = " "
        return self.embedding_service.get_embedding_vector(text)

    def delete_document(self, filename: str, owner: str, verbose: bool = True):
        """
        Delete all chunks of a document by filename and owner.
        Compatible with PDFVectorizer.delete_document.
        
        Args:
            filename: Document filename to delete
            owner: Owner of the document
            verbose: Whether to print progress
        """
        try:
            self._ensure_collection()
            
            scroll_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="filename", match=MatchValue(value=filename)),
                        FieldCondition(key="owner", match=MatchValue(value=owner))
                    ]
                ),
                limit=10000
            )
            
            points_to_delete = [point.id for point in scroll_result[0]]
            if points_to_delete:
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
                if verbose:
                    print(f"✓ Deleted {len(points_to_delete)} existing pages for: {filename} (owner: {owner})")
            else:
                if verbose:
                    print(f"✓ No existing pages found for: {filename} (owner: {owner})")
        except Exception as e:
            if verbose:
                print(f"⚠ Warning: Failed to delete existing pages: {e}")

    def vectorize_pdf(
        self,
        pdf_path: str,
        owner: str,
        display_filename: str = None,
        verbose: bool = True,
        progress_instance: VectorizationProgress = None,
        enable_summary: bool = False
    ) -> Dict:
        """
        Vectorize PDF file.
        Compatible with PDFVectorizer.vectorize_pdf interface.

        Args:
            pdf_path: Path to PDF file
            owner: Owner of the document
            display_filename: Optional display filename
            verbose: Whether to print progress
            progress_instance: Optional dedicated progress instance
            enable_summary: Whether to generate LLM summary (default: False)

        Returns:
            Dictionary with processing results
        """
        # Use provided progress instance or fall back to self.progress
        progress = progress_instance if progress_instance is not None else self.progress
        progress.reset()
        
        self._ensure_collection()
        
        filename = display_filename if display_filename else os.path.basename(pdf_path)
        
        try:
            progress.update(
                stage="init",
                message=f"开始处理文档: {filename}",
                current_step="初始化",
                progress_percent=0,
                data={"filename": filename, "owner": owner}
            )
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"Processing PDF: {filename}")
                print(f"Owner: {owner}")
                print(f"{'='*60}\n")
            
            # Delete existing
            progress.update(
                message="检查并删除已存在的文档",
                current_step="去重处理",
                progress_percent=5
            )
            if verbose:
                print("Step 0: Checking for duplicate documents...")
            self.delete_document(filename, owner, verbose)
            
            # Process PDF
            progress.update(
                stage="parsing",
                message="正在解析文档...",
                current_step="文档解析",
                progress_percent=5
            )

            if verbose:
                print("\nStep 1: Parsing PDF...")

            def parsing_callback(current, total, msg):
                percent = 5 + (current / total) * 10
                progress.update(
                    stage="parsing",
                    total_pages=total,
                    current_page=current,
                    message="正在解析文档",
                    current_step=f"解析第 {current}/{total} 页",
                    progress_percent=percent,
                    data={"parsed_pages": current, "total_pages": total}
                )
                if verbose:
                    print(f"  - Parsing: {current}/{total}")

            processor = self.processors[".pdf"]
            chunks = processor.process(
                pdf_path,
                progress_callback=parsing_callback,
                verbose=verbose,
                enable_summary=enable_summary
            )

            total_pages = len(chunks)
            progress.update(
                total_pages=total_pages,
                current_page=total_pages,
                message=f"文档解析完成，共 {total_pages} 页",
                progress_percent=15
            )
            
            if verbose:
                print(f"✓ Parsed {total_pages} pages\n")
            
            # Vectorize and store
            progress.update(stage="processing")
            points = []
            
            # Get max point_id
            try:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                if collection_info.points_count > 0:
                    scroll_result = self.qdrant_client.scroll(
                        collection_name=self.collection_name,
                        limit=10000,
                        with_payload=False,
                        with_vectors=False
                    )
                    existing_ids = [point.id for point in scroll_result[0]]
                    point_id = max(existing_ids) + 1 if existing_ids else 0
                else:
                    point_id = 0
            except Exception as e:
                if verbose:
                    print(f"⚠ Warning: Could not get max point_id, starting from 0: {e}")
                point_id = 0
            
            for i, chunk in enumerate(chunks):
                page_number = chunk.metadata["page_number"]
                page_progress = 15 + (page_number / total_pages) * 70
                
                progress.update(
                    current_page=page_number,
                    message="生成页面摘要",
                    current_step="生成摘要",
                    progress_percent=page_progress,
                    data={"page_number": page_number}
                )
                
                if verbose:
                    print(f"Processing Page {page_number}...")
                    print(f"  - Generating summary vector...")
                
                # Vectorize
                summary_vec = self._get_embedding(chunk.summary)
                
                progress.update(
                    current_step="内容向量化",
                    progress_percent=page_progress + (70 / total_pages * 0.6),
                    message="内容向量化"
                )
                
                if verbose:
                    print(f"  - Generating content vector...")
                
                content_vec = self._get_embedding(chunk.content)
                
                # Create point with PDFVectorizer-compatible payload structure
                point = PointStruct(
                    id=point_id,
                    vector={
                        "summary_vector": summary_vec,
                        "content_vector": content_vec
                    },
                    payload={
                        "owner": owner,
                        "filename": filename,
                        "page_number": page_number,
                        "summary": chunk.summary,
                        "content": chunk.content
                    }
                )
                points.append(point)
                point_id += 1
                
                progress.update(
                    current_step="页面处理完成",
                    progress_percent=page_progress + (70 / total_pages),
                    message="页面处理完成",
                    data={
                        "page_number": page_number,
                        "summary_length": len(chunk.summary),
                        "content_length": len(chunk.content)
                    }
                )
                
                if verbose:
                    print(f"  ✓ Page {page_number} processed (summary: {len(chunk.summary)} chars, content: {len(chunk.content)} chars)\n")
            
            # Store in Qdrant
            progress.update(
                stage="storing",
                current_page=total_pages,
                message=f"正在存储 {len(points)} 个向量到数据库...",
                current_step="数据存储",
                progress_percent=90,
                data={"total_vectors": len(points)}
            )
            
            if verbose:
                print(f"Storing {len(points)} vectors in Qdrant...")
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            # Completed
            final_result = {
                "filename": filename,
                "owner": owner,
                "total_pages": total_pages,
                "processed_pages": len(points),
                "collection": self.collection_name
            }
            
            progress.update(
                stage="completed",
                message=f"处理完成！成功存储 {len(points)} 页",
                current_step="完成",
                progress_percent=100,
                data=final_result
            )
            
            if verbose:
                print(f"✓ Successfully stored {len(points)} pages in Qdrant\n")
                print(f"{'='*60}")
                print(f"Processing complete!")
                print(f"{'='*60}\n")
            
            return final_result
            
        except Exception as e:
            error_msg = f"向量化失败: {str(e)}"
            if verbose:
                print(f"\n{'='*60}")
                print(f"ERROR: {error_msg}")
                print(f"{'='*60}\n")
            
            progress.update(
                stage="error",
                message=error_msg,
                error=str(e),
                progress_percent=0
            )
            
            raise

    def vectorize_file(
        self,
        file_path: str,
        owner: str,
        verbose: bool = True,
        **kwargs
    ) -> Dict:
        """
        Vectorize any supported file type.

        Args:
            file_path: Path to file
            owner: Owner identifier
            verbose: Print progress
            **kwargs: Processor-specific arguments
                - display_filename: Optional display filename
                - progress_instance: Optional progress tracker
                - enable_summary: bool (default False) - Enable LLM summary generation

                Excel-specific:
                - min_chinese_chars: int (default 250) - Minimum Chinese chars per chunk
                - summary_columns: List[str] - Column names to use as summary
        """
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Route to vectorize_pdf for PDF files
        if ext == ".pdf":
            return self.vectorize_pdf(
                file_path,
                owner,
                display_filename=kwargs.get("display_filename"),
                verbose=verbose,
                progress_instance=kwargs.get("progress_instance"),
                enable_summary=kwargs.get("enable_summary", False)
            )
        
        # Handle Excel files
        if ext not in [".xlsx", ".xls"]:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # Excel vectorization
        progress = kwargs.get("progress_instance") or self.progress
        progress.reset()
        
        display_filename = kwargs.get("display_filename") or filename
        chunk_size = kwargs.get("chunk_size", 0)
        summary_columns = kwargs.get("summary_columns")
        
        try:
            self._ensure_collection()
            
            progress.update(
                stage="init",
                message=f"开始处理Excel: {display_filename}",
                current_step="初始化",
                progress_percent=0,
                data={"filename": display_filename, "owner": owner}
            )
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"Processing Excel: {display_filename}")
                print(f"Owner: {owner}")
                if chunk_size > 0:
                    print(f"Chunk size: {chunk_size} chars")
                print(f"{'='*60}\n")
            
            # Delete existing
            progress.update(
                message="检查并删除已存在的文档",
                current_step="去重处理",
                progress_percent=5
            )
            self.delete_document(display_filename, owner, verbose)
            
            # Process Excel
            progress.update(
                stage="parsing",
                message="正在解析文档...",
                current_step="文档解析",
                progress_percent=10
            )

            if verbose:
                print("Step 1: Parsing Excel...")

            def excel_callback(current, total, msg):
                percent = 10 + (current / total) * 30
                progress.update(
                    stage="parsing",
                    total_pages=total,  # 使用 total_pages 保持兼容性
                    current_page=current,
                    message="正在解析文档行",
                    current_step=f"处理第 {current}/{total} 行",
                    progress_percent=percent,
                    data={"parsed_rows": current, "total_rows": total}
                )

            processor = self.processors[ext]
            chunks = processor.process(
                file_path,
                min_chinese_chars=kwargs.get("min_chinese_chars", 250),
                summary_columns=summary_columns,
                enable_summary=kwargs.get("enable_summary", False),
                progress_callback=excel_callback
            )

            total_chunks = len(chunks)
            progress.update(
                total_pages=total_chunks,
                current_page=total_chunks,
                message=f"文档解析完成，共 {total_chunks} 个数据块",
                progress_percent=40
            )
            
            if verbose:
                print(f"✓ Parsed {total_chunks} chunks\n")
            
            # Vectorize and store
            progress.update(stage="processing")
            points = []
            
            # Get max point_id
            try:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                if collection_info.points_count > 0:
                    scroll_result = self.qdrant_client.scroll(
                        collection_name=self.collection_name,
                        limit=10000,
                        with_payload=False,
                        with_vectors=False
                    )
                    existing_ids = [point.id for point in scroll_result[0]]
                    point_id = max(existing_ids) + 1 if existing_ids else 0
                else:
                    point_id = 0
            except Exception as e:
                if verbose:
                    print(f"⚠ Warning: Could not get max point_id, starting from 0: {e}")
                point_id = 0
            
            for i, chunk in enumerate(chunks):
                chunk_progress = 40 + (i / total_chunks) * 50
                
                progress.update(
                    current_page=i + 1,
                    message="向量化数据块",
                    current_step=f"向量化 {i+1}/{total_chunks}",
                    progress_percent=chunk_progress,
                    data={"chunk_number": i + 1}
                )
                
                if verbose and i % 10 == 0:
                    print(f"Processing chunk {i+1}/{total_chunks}...")
                
                # Vectorize
                summary_vec = self._get_embedding(chunk.summary)
                content_vec = self._get_embedding(chunk.content)
                
                # For Excel, we need to adapt the payload structure
                # Use row_number instead of page_number for Excel
                row_info = chunk.metadata.get("row_number") or chunk.metadata.get("start_row", i)
                
                # Create point - keep page_number for compatibility
                point = PointStruct(
                    id=point_id,
                    vector={
                        "summary_vector": summary_vec,
                        "content_vector": content_vec
                    },
                    payload={
                        "owner": owner,
                        "filename": display_filename,
                        "page_number": row_info,  # 使用行号作为 page_number 保持兼容性
                        "summary": chunk.summary,
                        "content": chunk.content,
                        **{k: v for k, v in chunk.metadata.items() if k not in ["row_number", "start_row", "end_row"]}
                    }
                )
                points.append(point)
                point_id += 1
            
            # Store in Qdrant
            progress.update(
                stage="storing",
                current_page=total_chunks,
                message=f"正在存储 {len(points)} 个向量到数据库...",
                current_step="数据存储",
                progress_percent=90,
                data={"total_vectors": len(points)}
            )
            
            if verbose:
                print(f"Storing {len(points)} vectors in Qdrant...")
            
            # Batch upsert
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i+batch_size]
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            
            # Completed
            final_result = {
                "filename": display_filename,
                "owner": owner,
                "total_pages": total_chunks,  # 保持字段名兼容性
                "processed_pages": len(points),
                "collection": self.collection_name,
                "file_type": "excel"
            }
            
            progress.update(
                stage="completed",
                message=f"处理完成！成功存储 {len(points)} 个数据块",
                current_step="完成",
                progress_percent=100,
                data=final_result
            )
            
            if verbose:
                print(f"✓ Successfully stored {len(points)} chunks in Qdrant\n")
                print(f"{'='*60}")
                print(f"Processing complete!")
                print(f"{'='*60}\n")
            
            return final_result
            
        except Exception as e:
            error_msg = f"向量化失败: {str(e)}"
            if verbose:
                print(f"\n{'='*60}")
                print(f"ERROR: {error_msg}")
                print(f"{'='*60}\n")
            
            progress.update(
                stage="error",
                message=error_msg,
                error=str(e),
                progress_percent=0
            )
            
            raise

    def search(
        self,
        query: str,
        limit: int = 5,
        mode: str = "dual",
        owner: Optional[str] = None,
        verbose: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Search similar pages by query.
        Compatible with PDFVectorizer.search interface.
        
        Args:
            query: Search query
            limit: Number of results to return per path
            mode: Retrieval mode - "dual" (both), "summary" (summary only), "content" (content only)
            owner: Optional owner filter
            verbose: Whether to print results
            
        Returns:
            Dictionary with keys depending on mode:
            - mode="dual": {"summary_results": [...], "content_results": [...]}
            - mode="summary": {"summary_results": [...]}
            - mode="content": {"content_results": [...]}
        """
        if mode not in ["dual", "summary", "content"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'dual', 'summary', or 'content'.")
        
        query_embedding = self._get_embedding(query)
        
        # Build filter
        search_filter = None
        if owner is not None:
            search_filter = Filter(
                must=[
                    FieldCondition(key="owner", match=MatchValue(value=owner))
                ]
            )
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"Mode: {mode.upper()}")
            if owner:
                print(f"Owner filter: {owner}")
            print(f"{'='*60}\n")
        
        results = {}
        
        # Path 1: Search using summary_vector
        if mode in ["dual", "summary"]:
            if verbose:
                print("🔍 Searching via SUMMARY vector...")
            summary_search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=("summary_vector", query_embedding),
                limit=limit,
                query_filter=search_filter
            )
            
            summary_results = []
            for i, hit in enumerate(summary_search_results, 1):
                result = {
                    "rank": i,
                    "score": hit.score,
                    "filename": hit.payload["filename"],
                    "page_number": hit.payload["page_number"],
                    "summary": hit.payload["summary"],
                    "content": hit.payload["content"],
                    "retrieval_path": "summary"
                }
                summary_results.append(result)
                
                if verbose:
                    print(f"\n  Result #{i} (Score: {hit.score:.4f})")
                    print(f"  File: {result['filename']}, Page: {result['page_number']}")
                    print(f"  Summary: {result['summary'][:100]}...")
            
            results["summary_results"] = summary_results
        
        # Path 2: Search using content_vector
        if mode in ["dual", "content"]:
            if verbose and mode == "dual":
                print(f"\n\n🔍 Searching via CONTENT vector...")
            elif verbose:
                print("🔍 Searching via CONTENT vector...")
            
            content_search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=("content_vector", query_embedding),
                limit=limit,
                query_filter=search_filter
            )
            
            content_results = []
            for i, hit in enumerate(content_search_results, 1):
                result = {
                    "rank": i,
                    "score": hit.score,
                    "filename": hit.payload["filename"],
                    "page_number": hit.payload["page_number"],
                    "summary": hit.payload["summary"],
                    "content": hit.payload["content"],
                    "retrieval_path": "content"
                }
                content_results.append(result)
                
                if verbose:
                    print(f"\n  Result #{i} (Score: {hit.score:.4f})")
                    print(f"  File: {result['filename']}, Page: {result['page_number']}")
                    print(f"  Summary: {result['summary'][:100]}...")
            
            results["content_results"] = content_results
        
        if verbose:
            print(f"\n{'='*60}")
            if "summary_results" in results:
                print(f"Summary path: {len(results['summary_results'])} results")
            if "content_results" in results:
                print(f"Content path: {len(results['content_results'])} results")
            print(f"{'='*60}\n")
        
        return results

    def get_pages(
        self,
        filename: str,
        page_numbers: List[int],
        fields: Optional[List[str]] = None,
        owner: Optional[str] = None,
        verbose: bool = False
    ) -> List[Dict]:
        """
        Get page slices by filename and page numbers.
        Compatible with PDFVectorizer.get_pages interface.
        
        Args:
            filename: Document filename
            page_numbers: List of page numbers to retrieve
            fields: List of fields to return. If None, returns all fields.
            owner: Optional owner filter
            verbose: Whether to print progress
            
        Returns:
            List of dictionaries containing requested fields for each page
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Retrieving pages from: {filename}")
            print(f"Page numbers: {page_numbers}")
            print(f"Fields: {fields or 'all'}")
            if owner:
                print(f"Owner filter: {owner}")
            print(f"{'='*60}\n")
        
        # Available fields in payload
        available_fields = {"filename", "page_number", "summary", "content", "owner"}
        
        # If no fields specified, return all
        if fields is None:
            fields = list(available_fields)
        else:
            # Validate requested fields
            invalid_fields = set(fields) - available_fields
            if invalid_fields:
                raise ValueError(f"Invalid fields: {invalid_fields}. Available fields: {available_fields}")
        
        results = []
        
        # Query each page number
        for page_num in page_numbers:
            try:
                # Build filter conditions
                filter_conditions = [
                    FieldCondition(key="filename", match=MatchValue(value=filename)),
                    FieldCondition(key="page_number", match=MatchValue(value=page_num))
                ]
                
                # Add owner filter if provided
                if owner:
                    filter_conditions.append(
                        FieldCondition(key="owner", match=MatchValue(value=owner))
                    )
                
                # Search for this specific page
                scroll_result = self.qdrant_client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(must=filter_conditions),
                    limit=1
                )
                
                # If page found, extract requested fields
                if scroll_result[0]:
                    point = scroll_result[0][0]
                    page_data = {}
                    
                    for field in fields:
                        if field in point.payload:
                            page_data[field] = point.payload[field]
                    
                    results.append(page_data)
                    
                    if verbose:
                        print(f"✓ Found page {page_num}")
                else:
                    if verbose:
                        print(f"✗ Page {page_num} not found")
            
            except Exception as e:
                if verbose:
                    print(f"✗ Error retrieving page {page_num}: {e}")
                continue
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Retrieved {len(results)} out of {len(page_numbers)} requested pages")
            print(f"{'='*60}\n")
        
        return results
