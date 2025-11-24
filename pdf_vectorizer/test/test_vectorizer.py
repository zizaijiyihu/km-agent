"""
测试 PDFVectorizer 的所有对外方法
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pdf_vectorizer import PDFVectorizer


def test_all_methods():
    """测试所有对外方法"""

    # 初始化
    print("=" * 60)
    print("初始化 PDFVectorizer")
    print("=" * 60)

    vectorizer = PDFVectorizer(
        collection_name="test_pdf_collection",
        vector_size=4096
    )

    # 测试PDF路径
    pdf_path = os.path.join(os.path.dirname(__file__), "居住证办理.pdf")
    owner = "test_user"

    # 1. 测试 vectorize_pdf
    print("\n" + "=" * 60)
    print("测试 1: vectorize_pdf()")
    print("=" * 60)

    result = vectorizer.vectorize_pdf(
        pdf_path=pdf_path,
        owner=owner,
        display_filename="居住证办理.pdf",
        verbose=True
    )
    print(f"\n向量化结果: {result}")

    # 2. 测试 search (双路径模式)
    print("\n" + "=" * 60)
    print("测试 2: search() - dual mode")
    print("=" * 60)

    search_results = vectorizer.search(
        query="居住证如何办理",
        limit=3,
        mode="dual",
        owner=owner,
        verbose=True
    )

    # 3. 测试 search (仅摘要模式)
    print("\n" + "=" * 60)
    print("测试 3: search() - summary mode")
    print("=" * 60)

    summary_results = vectorizer.search(
        query="需要什么材料",
        limit=2,
        mode="summary",
        owner=owner,
        verbose=True
    )

    # 4. 测试 search (仅内容模式)
    print("\n" + "=" * 60)
    print("测试 4: search() - content mode")
    print("=" * 60)

    content_results = vectorizer.search(
        query="办理流程",
        limit=2,
        mode="content",
        owner=owner,
        verbose=True
    )

    # 5. 测试 get_pages
    print("\n" + "=" * 60)
    print("测试 5: get_pages()")
    print("=" * 60)

    pages = vectorizer.get_pages(
        filename="居住证办理.pdf",
        page_numbers=[1, 2],
        fields=["page_number", "summary", "content"],
        owner=owner,
        verbose=True
    )

    for page in pages:
        print(f"\n第 {page.get('page_number')} 页:")
        print(f"  摘要: {page.get('summary', '')[:100]}...")
        print(f"  内容长度: {len(page.get('content', ''))} 字符")

    # 6. 测试 delete_document
    print("\n" + "=" * 60)
    print("测试 6: delete_document()")
    print("=" * 60)

    vectorizer.delete_document(
        filename="居住证办理.pdf",
        owner=owner,
        verbose=True
    )

    # 7. 验证删除成功
    print("\n" + "=" * 60)
    print("验证删除: 再次搜索应该无结果")
    print("=" * 60)

    verify_results = vectorizer.search(
        query="居住证",
        limit=3,
        mode="summary",
        owner=owner,
        verbose=True
    )

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_all_methods()
