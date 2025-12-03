import os
import sys
import pandas as pd
import uuid
import re
from typing import List, Dict, Any
from .base import BaseProcessor
from ..domain import DocumentChunk

# Import ks_infrastructure services for LLM summary if needed
# We need to add project root to path to import ks_infrastructure
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ks_infrastructure import ks_openai
from ks_infrastructure.configs.default import OPENAI_CONFIG

class ExcelProcessor(BaseProcessor):
    """Processor for Excel files."""

    def __init__(self):
        self.llm_client = ks_openai()
        self.llm_model = OPENAI_CONFIG.get("model", "DeepSeek-V3.1-Ksyun")

    def _count_chinese_chars(self, text: str) -> int:
        """Count Chinese characters only (excluding English, numbers, punctuation)."""
        return len(re.findall(r'[\u4e00-\u9fff]', text))

    def _generate_summary(self, content: str) -> str:
        """Generate summary using LLM."""
        try:
            prompt = f"""请为以下Excel数据生成一个简洁的摘要（50-100字）。
摘要应该：
1. 概括核心信息
2. 如果是问答数据，重点提取问题和核心答案
3. 忽略无关的ID或格式信息

数据内容：
{content}

请直接输出摘要。"""

            completion = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个数据分析助手。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Summary generation failed: {e}")
            return content[:200]

    def process(self, file_path: str, **kwargs) -> List[DocumentChunk]:
        """
        Process Excel file with intelligent Chinese-character-based chunking.

        kwargs:
            min_chinese_chars: int (default 250) - Minimum Chinese characters per chunk
            summary_columns: List[str] (default None) - Columns to use for summary
            enable_summary: bool (default False) - Whether to generate LLM summary
            progress_callback: Callable (optional)
        """
        min_chinese_chars = kwargs.get("min_chinese_chars", 250)
        summary_columns = kwargs.get("summary_columns")
        enable_summary = kwargs.get("enable_summary", False)
        progress_callback = kwargs.get("progress_callback")

        df = pd.read_excel(file_path)
        df = df.fillna('')
        total_rows = len(df)

        chunks = []
        current_chunk_rows = []
        current_chinese_chars = 0

        for index, row in df.iterrows():
            row_dict = row.to_dict()

            # Construct Content
            content_parts = []
            for k, v in row_dict.items():
                if str(v).strip():
                    content_parts.append(f"{k}: {v}")
            content_text = "\n".join(content_parts)

            if not content_text.strip():
                continue

            row_chinese_chars = self._count_chinese_chars(content_text)

            # Case 1: Single row has >= min_chinese_chars → Flush accumulated + Create single-row chunk
            if row_chinese_chars >= min_chinese_chars:
                # Flush accumulated rows first
                if current_chunk_rows:
                    chunks.append(self._create_chunk(current_chunk_rows, summary_columns, enable_summary))
                    current_chunk_rows = []
                    current_chinese_chars = 0

                # Create chunk for this single row
                chunks.append(self._create_chunk([{
                    "index": index,
                    "content": content_text,
                    "data": row_dict
                }], summary_columns, enable_summary))

            # Case 2: Single row has < min_chinese_chars → Accumulate
            else:
                current_chunk_rows.append({
                    "index": index,
                    "content": content_text,
                    "data": row_dict
                })
                current_chinese_chars += row_chinese_chars

                # Flush when accumulated Chinese chars >= threshold
                if current_chinese_chars >= min_chinese_chars:
                    chunks.append(self._create_chunk(current_chunk_rows, summary_columns, enable_summary))
                    current_chunk_rows = []
                    current_chinese_chars = 0

            if progress_callback and index % 10 == 0:
                progress_callback(index, total_rows, "Processing Excel rows")

        # Flush remaining rows (even if < min_chinese_chars)
        if current_chunk_rows:
            chunks.append(self._create_chunk(current_chunk_rows, summary_columns, enable_summary))

        return chunks

    def _create_chunk(self, rows: List[Dict], summary_columns: List[str] = None, enable_summary: bool = False) -> DocumentChunk:
        combined_content = "\n\n".join([r["content"] for r in rows])
        row_indices = [r["index"] for r in rows]
        start_row = min(row_indices)
        end_row = max(row_indices)

        # Generate Summary (default: disabled)
        if summary_columns:
            # Use specified columns as summary
            summary_parts = []
            for item in rows:
                row_parts = []
                for col in summary_columns:
                    val = item["data"].get(col)
                    if val and str(val).strip():
                        row_parts.append(str(val))
                if row_parts:
                    summary_parts.append(" ".join(row_parts))
            summary = "\n".join(summary_parts)
            if not summary:
                summary = combined_content[:200]
        elif enable_summary:
            # Generate summary using LLM (only if enabled)
            summary = self._generate_summary(combined_content)
        else:
            # Default: Use first 200 chars as summary
            summary = combined_content[:200]

        # Metadata
        metadata = {
            "start_row": start_row,
            "end_row": end_row,
            "row_count": len(rows),
            "type": "excel_chunk" if len(rows) > 1 else "excel_row",
            "chinese_chars": self._count_chinese_chars(combined_content)
        }

        # If single row, add all columns to metadata
        if len(rows) == 1:
            row_data = rows[0]["data"]
            metadata.update({f"col_{k}": str(v) for k, v in row_data.items()})
            metadata["row_number"] = start_row

        return DocumentChunk(
            content=combined_content,
            summary=summary,
            metadata=metadata,
            chunk_id=str(uuid.uuid4())
        )
