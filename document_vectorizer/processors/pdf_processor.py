import os
import sys
import uuid
from typing import List, Dict, Any
from .base import BaseProcessor
from ..domain import DocumentChunk

# Import pdf_to_json and infrastructure
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pdf_to_json import PDFToJSONConverter
from ks_infrastructure import ks_openai
from ks_infrastructure.configs.default import OPENAI_CONFIG

class PDFProcessor(BaseProcessor):
    """Processor for PDF files."""
    
    def __init__(self):
        self.pdf_converter = PDFToJSONConverter()
        self.llm_client = ks_openai()
        self.llm_model = OPENAI_CONFIG.get("model", "DeepSeek-V3.1-Ksyun")

    def _generate_summary(self, page_content: str, page_number: int) -> str:
        """Generate summary for a page using LLM."""
        try:
            prompt = f"""请为以下PDF第{page_number}页的内容生成一个简洁的摘要（100-200字）。
摘要应该：
1. 提取关键信息和主要观点
2. 保留重要的数据和结论
3. 忽略格式和样式信息
4. 使用简洁的语言

页面内容：
{page_content}

请直接输出摘要，不需要前缀说明。"""

            completion = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档摘要助手。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"生成摘要失败: {str(e)}"

    def process(self, file_path: str, **kwargs) -> List[DocumentChunk]:
        """
        Process PDF file.
        kwargs:
            progress_callback: Callable (optional)
            verbose: bool (default True)
            enable_summary: bool (default False) - Whether to generate LLM summary
        """
        verbose = kwargs.get("verbose", True)
        progress_callback = kwargs.get("progress_callback")
        enable_summary = kwargs.get("enable_summary", False)
        
        # 1. Parse PDF
        def parsing_callback(current, total, msg):
            if progress_callback:
                progress_callback(current, total, f"Parsing PDF: {current}/{total}")

        result = self.pdf_converter.convert(
            file_path, 
            analyze_images=True, 
            verbose=verbose,
            progress_callback=parsing_callback
        )
        
        total_pages = result['total_pages']
        chunks = []
        
        # 2. Process Pages
        for page in result['pages']:
            page_number = page['page_number']
            paragraphs = page['paragraphs']
            page_content = "\n\n".join(paragraphs)

            if not page_content.strip():
                continue

            if progress_callback:
                progress_callback(page_number, total_pages, f"Processing page {page_number}")

            # Generate summary only if enabled (default: disabled)
            if enable_summary:
                summary = self._generate_summary(page_content, page_number)
            else:
                # Default: Use first 200 chars as summary
                summary = page_content[:200]

            chunk = DocumentChunk(
                content=page_content,
                summary=summary,
                metadata={
                    "page_number": page_number,
                    "type": "pdf_page"
                },
                chunk_id=str(uuid.uuid4())
            )
            chunks.append(chunk)

        return chunks
