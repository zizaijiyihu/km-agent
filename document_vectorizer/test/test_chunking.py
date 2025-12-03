"""
测试文档切块逻辑和摘要生成功能

测试重点：
1. Excel 按中文字符数智能切块（默认250字）
2. PDF 和 Excel 默认关闭 LLM 摘要生成
3. 进度提示语通用化（不硬编码文件类型）
"""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from document_vectorizer.vectorizer import DocumentVectorizer

def test_excel_chunking():
    """测试 Excel 智能切块逻辑"""
    print("\n" + "="*80)
    print("测试 1: Excel 中文字符智能切块")
    print("="*80)

    excel_path = "/Users/xiaohu/projects/km-agent_2/document_vectorizer/test/金山云HR服务台_问答库_20251010.xlsx"

    if not os.path.exists(excel_path):
        print(f"❌ 测试文件不存在: {excel_path}")
        return

    vectorizer = DocumentVectorizer(collection_name="test_chunking_kb")
    owner = "test_chunking_user"

    print(f"\n📄 测试文件: {os.path.basename(excel_path)}")
    print(f"👤 Owner: {owner}")

    # 测试 1: 默认参数（250中文字符，不生成摘要）
    print("\n--- 场景 1: 默认参数（min_chinese_chars=250, enable_summary=False）---")
    try:
        result = vectorizer.vectorize_file(
            excel_path,
            owner,
            verbose=True
        )
        print(f"\n✅ 处理结果:")
        print(f"   文件名: {result['filename']}")
        print(f"   总块数: {result['total_pages']}")
        print(f"   处理块数: {result['processed_pages']}")
        print(f"   Collection: {result['collection']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    # 测试 2: 自定义阈值（300中文字符）
    print("\n--- 场景 2: 自定义阈值（min_chinese_chars=300）---")
    try:
        result = vectorizer.vectorize_file(
            excel_path,
            owner,
            min_chinese_chars=300,
            verbose=True
        )
        print(f"\n✅ 处理结果:")
        print(f"   总块数: {result['total_pages']}")
        print(f"   处理块数: {result['processed_pages']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")

    # 测试 3: 启用 LLM 摘要
    print("\n--- 场景 3: 启用 LLM 摘要（enable_summary=True）---")
    try:
        result = vectorizer.vectorize_file(
            excel_path,
            owner,
            min_chinese_chars=250,
            enable_summary=True,  # 启用 LLM 摘要
            verbose=True
        )
        print(f"\n✅ 处理结果:")
        print(f"   总块数: {result['total_pages']}")
        print(f"   处理块数: {result['processed_pages']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")

    # 测试 4: 指定摘要列
    print("\n--- 场景 4: 指定摘要列（summary_columns=['标准问题']）---")
    try:
        result = vectorizer.vectorize_file(
            excel_path,
            owner,
            min_chinese_chars=250,
            summary_columns=["标准问题"],
            verbose=True
        )
        print(f"\n✅ 处理结果:")
        print(f"   总块数: {result['total_pages']}")
        print(f"   处理块数: {result['processed_pages']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")

    # 查询验证
    print("\n--- 查询验证 ---")
    try:
        search_results = vectorizer.search(
            "社保公积金",
            limit=3,
            owner=owner,
            verbose=True
        )

        print("\n检查摘要内容（验证是否调用了LLM）:")
        for result_type, items in search_results.items():
            print(f"\n{result_type}:")
            for i, item in enumerate(items[:2], 1):
                print(f"  结果 {i}:")
                print(f"    文件: {item['filename']}")
                print(f"    页码/行号: {item['page_number']}")
                print(f"    摘要: {item['summary'][:150]}...")
                print(f"    内容: {item['content'][:150]}...")
    except Exception as e:
        print(f"\n❌ 查询错误: {e}")


def test_pdf_summary():
    """测试 PDF 默认关闭摘要"""
    print("\n" + "="*80)
    print("测试 2: PDF 默认关闭 LLM 摘要")
    print("="*80)

    pdf_path = "/Users/xiaohu/projects/km-agent_2/document_vectorizer/test/居住证办理.pdf"

    if not os.path.exists(pdf_path):
        print(f"❌ 测试文件不存在: {pdf_path}")
        return

    vectorizer = DocumentVectorizer(collection_name="test_pdf_summary_kb")
    owner = "test_pdf_user"

    print(f"\n📄 测试文件: {os.path.basename(pdf_path)}")
    print(f"👤 Owner: {owner}")

    # 测试 1: 默认不生成摘要
    print("\n--- 场景 1: 默认参数（enable_summary=False）---")
    try:
        result = vectorizer.vectorize_pdf(
            pdf_path,
            owner,
            verbose=True
        )
        print(f"\n✅ 处理结果:")
        print(f"   文件名: {result['filename']}")
        print(f"   总页数: {result['total_pages']}")
        print(f"   处理页数: {result['processed_pages']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    # 测试 2: 启用 LLM 摘要
    print("\n--- 场景 2: 启用 LLM 摘要（enable_summary=True）---")
    try:
        result = vectorizer.vectorize_pdf(
            pdf_path,
            owner,
            enable_summary=True,
            verbose=True
        )
        print(f"\n✅ 处理结果:")
        print(f"   总页数: {result['total_pages']}")
        print(f"   处理页数: {result['processed_pages']}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")

    # 查询验证
    print("\n--- 查询验证 ---")
    try:
        search_results = vectorizer.search(
            "居住证",
            limit=2,
            owner=owner,
            verbose=True
        )

        print("\n检查摘要内容:")
        for result_type, items in search_results.items():
            print(f"\n{result_type}:")
            for i, item in enumerate(items, 1):
                print(f"  结果 {i}:")
                print(f"    页码: {item['page_number']}")
                print(f"    摘要: {item['summary'][:150]}...")
    except Exception as e:
        print(f"\n❌ 查询错误: {e}")


def test_progress_messages():
    """测试进度提示语通用化"""
    print("\n" + "="*80)
    print("测试 3: 进度提示语通用化（无硬编码文件类型）")
    print("="*80)

    from document_vectorizer.vectorizer import VectorizationProgress

    vectorizer = DocumentVectorizer(collection_name="test_progress_kb")
    owner = "test_progress_user"

    # 创建专用进度对象
    progress = VectorizationProgress()

    excel_path = "/Users/xiaohu/projects/km-agent_2/document_vectorizer/test/金山云HR服务台_问答库_20251010.xlsx"
    pdf_path = "/Users/xiaohu/projects/km-agent_2/document_vectorizer/test/居住证办理.pdf"

    print("\n--- Excel 处理进度 ---")
    if os.path.exists(excel_path):
        try:
            # 使用 verbose=False 来只看进度对象
            import threading
            import time

            def monitor_progress():
                """监控进度变化"""
                last_message = ""
                while not progress.is_completed and not progress.is_error:
                    current_progress = progress.get()
                    message = current_progress.get('message', '')
                    if message and message != last_message:
                        print(f"  📊 进度: {message} ({current_progress.get('progress_percent', 0):.1f}%)")
                        last_message = message
                    time.sleep(0.1)

            # 启动监控线程
            monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
            monitor_thread.start()

            result = vectorizer.vectorize_file(
                excel_path,
                owner,
                progress_instance=progress,
                verbose=False
            )

            # 等待监控完成
            time.sleep(0.5)

            print(f"\n  ✅ Excel 处理完成")

            # 检查进度消息中是否有硬编码的 "Excel" 或 "PDF"
            final_progress = progress.get()
            print(f"\n  最终进度消息: {final_progress.get('message')}")

        except Exception as e:
            print(f"\n  ❌ 错误: {e}")

    print("\n--- PDF 处理进度 ---")
    if os.path.exists(pdf_path):
        try:
            progress.reset()

            # 启动监控线程
            monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
            monitor_thread.start()

            result = vectorizer.vectorize_pdf(
                pdf_path,
                owner,
                progress_instance=progress,
                verbose=False
            )

            # 等待监控完成
            time.sleep(0.5)

            print(f"\n  ✅ PDF 处理完成")

            # 检查进度消息
            final_progress = progress.get()
            print(f"\n  最终进度消息: {final_progress.get('message')}")

        except Exception as e:
            print(f"\n  ❌ 错误: {e}")


if __name__ == "__main__":
    print("\n" + "🚀 开始文档切块和摘要功能测试\n")

    try:
        # 测试 1: Excel 智能切块
        test_excel_chunking()

        # 测试 2: PDF 摘要控制
        test_pdf_summary()

        # 测试 3: 进度提示语
        test_progress_messages()

        print("\n" + "="*80)
        print("✅ 所有测试完成")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
