"""
简单测试：只测试切块逻辑，不执行向量化

测试重点：
1. Excel 按中文字符数智能切块
2. 验证切块结果的正确性
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from document_vectorizer.processors.excel_processor import ExcelProcessor
from document_vectorizer.processors.pdf_processor import PDFProcessor

def test_excel_chinese_chunking():
    """测试 Excel 中文字符切块逻辑"""
    print("\n" + "="*80)
    print("测试 1: Excel 中文字符智能切块")
    print("="*80)

    excel_path = "/Users/xiaohu/projects/km-agent_2/document_vectorizer/test/金山云HR服务台_问答库_20251010.xlsx"

    if not os.path.exists(excel_path):
        print(f"❌ 测试文件不存在: {excel_path}")
        return

    processor = ExcelProcessor()

    # 场景 1: 默认 250 中文字符
    print("\n--- 场景 1: min_chinese_chars=250 (默认) ---")
    try:
        chunks = processor.process(
            excel_path,
            min_chinese_chars=250,
            enable_summary=False
        )

        print(f"✅ 生成了 {len(chunks)} 个 chunks")

        # 检查前几个 chunk
        for i, chunk in enumerate(chunks[:5], 1):
            chinese_chars = chunk.metadata.get('chinese_chars', 0)
            row_count = chunk.metadata.get('row_count', 1)
            chunk_type = chunk.metadata.get('type', 'unknown')

            print(f"\nChunk {i}:")
            print(f"  类型: {chunk_type}")
            print(f"  行数: {row_count}")
            print(f"  中文字符数: {chinese_chars}")
            print(f"  摘要长度: {len(chunk.summary)}")
            print(f"  内容长度: {len(chunk.content)}")
            print(f"  摘要前100字: {chunk.summary[:100]}...")

        # 统计
        single_row_chunks = sum(1 for c in chunks if c.metadata.get('row_count', 1) == 1)
        multi_row_chunks = sum(1 for c in chunks if c.metadata.get('row_count', 1) > 1)

        print(f"\n📊 统计:")
        print(f"  单行块: {single_row_chunks}")
        print(f"  多行块: {multi_row_chunks}")
        print(f"  总块数: {len(chunks)}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    # 场景 2: 自定义 300 中文字符
    print("\n--- 场景 2: min_chinese_chars=300 ---")
    try:
        chunks = processor.process(
            excel_path,
            min_chinese_chars=300,
            enable_summary=False
        )

        print(f"✅ 生成了 {len(chunks)} 个 chunks")

        single_row_chunks = sum(1 for c in chunks if c.metadata.get('row_count', 1) == 1)
        multi_row_chunks = sum(1 for c in chunks if c.metadata.get('row_count', 1) > 1)

        print(f"\n📊 统计:")
        print(f"  单行块: {single_row_chunks}")
        print(f"  多行块: {multi_row_chunks}")
        print(f"  总块数: {len(chunks)}")

    except Exception as e:
        print(f"❌ 错误: {e}")

    # 场景 3: 指定摘要列
    print("\n--- 场景 3: 使用摘要列 (summary_columns=['标准问题']) ---")
    try:
        chunks = processor.process(
            excel_path,
            min_chinese_chars=250,
            summary_columns=["标准问题"],
            enable_summary=False
        )

        print(f"✅ 生成了 {len(chunks)} 个 chunks")

        # 检查摘要是否来自指定列
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\nChunk {i} 摘要: {chunk.summary[:150]}...")

    except Exception as e:
        print(f"❌ 错误: {e}")


def test_pdf_summary_disabled():
    """测试 PDF 默认关闭摘要生成"""
    print("\n" + "="*80)
    print("测试 2: PDF 默认关闭 LLM 摘要")
    print("="*80)

    pdf_path = "/Users/xiaohu/projects/km-agent_2/document_vectorizer/test/居住证办理.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ 测试文件不存在: {pdf_path}")
        return

    processor = PDFProcessor()

    # 场景 1: 默认不生成摘要
    print("\n--- 场景 1: enable_summary=False (默认) ---")
    try:
        chunks = processor.process(
            pdf_path,
            enable_summary=False,
            verbose=True
        )

        print(f"\n✅ 生成了 {len(chunks)} 个页面 chunks")

        # 检查摘要内容（应该是前200字符，不是LLM生成）
        for i, chunk in enumerate(chunks[:3], 1):
            page_num = chunk.metadata.get('page_number', 0)
            print(f"\n页面 {page_num}:")
            print(f"  摘要长度: {len(chunk.summary)}")
            print(f"  内容长度: {len(chunk.content)}")
            print(f"  摘要: {chunk.summary[:100]}...")

            # 验证摘要是否就是内容的前200字符
            is_prefix = chunk.summary == chunk.content[:200]
            print(f"  摘要是内容前缀: {'✅ 是' if is_prefix else '❌ 否（可能是LLM生成）'}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def test_chinese_char_counting():
    """测试中文字符计数逻辑"""
    print("\n" + "="*80)
    print("测试 3: 中文字符计数逻辑")
    print("="*80)

    processor = ExcelProcessor()

    test_cases = [
        ("纯中文", 3),
        ("hello", 0),
        ("hello你好world", 2),
        ("中文123English", 2),
        ("问题：如何办理社保？", 8),  # 不含标点、数字、英文
        ("", 0),
    ]

    print("\n测试用例:")
    for text, expected in test_cases:
        count = processor._count_chinese_chars(text)
        status = "✅" if count == expected else "❌"
        print(f"{status} '{text}' -> 期望: {expected}, 实际: {count}")


if __name__ == "__main__":
    print("\n🚀 开始简单切块测试\n")

    try:
        # 测试 1: 中文字符计数
        test_chinese_char_counting()

        # 测试 2: Excel 智能切块
        test_excel_chinese_chunking()

        # 测试 3: PDF 摘要关闭
        test_pdf_summary_disabled()

        print("\n" + "="*80)
        print("✅ 所有测试完成")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
