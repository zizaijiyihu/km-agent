"""
清空pdf_vectorizer相关的数据库数据

功能：
- 清空Qdrant中的pdf_knowledge_base collection的所有数据
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ks_infrastructure import ks_qdrant
from qdrant_client.models import Filter


def clear_qdrant_collection(collection_name: str = "pdf_knowledge_base"):
    """
    清空Qdrant collection中的所有数据

    Args:
        collection_name: collection名称，默认为'pdf_knowledge_base'
    """
    print(f"\n{'='*60}")
    print(f"清空Qdrant Collection: {collection_name}")
    print(f"{'='*60}\n")

    try:
        client = ks_qdrant()

        # 检查collection是否存在
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if collection_name not in collection_names:
            print(f"⚠ Collection '{collection_name}' 不存在，无需清空")
            return

        # 获取collection信息
        collection_info = client.get_collection(collection_name)
        points_count = collection_info.points_count

        print(f"找到 {points_count} 条记录")

        if points_count == 0:
            print("✓ Collection已经是空的")
            return

        # 确认删除
        confirm = input(f"\n⚠️  确定要删除 {points_count} 条记录吗？(yes/no): ")
        if confirm.lower() != 'yes':
            print("✗ 操作已取消")
            return

        # 删除collection中的所有点
        # 使用delete方法删除所有满足条件的点（空filter表示匹配所有）
        client.delete(
            collection_name=collection_name,
            points_selector=Filter()  # 空filter匹配所有点
        )

        print(f"✓ 成功清空 collection '{collection_name}'")

        # 验证清空结果
        collection_info_after = client.get_collection(collection_name)
        print(f"✓ 当前记录数: {collection_info_after.points_count}")

    except Exception as e:
        print(f"✗ 清空失败: {e}")
        raise


def main():
    """主函数"""
    print("\n" + "="*60)
    print("PDF Vectorizer 数据库清空工具")
    print("="*60)
    print("\n此脚本将清空以下数据：")
    print("  - Qdrant: pdf_knowledge_base collection")
    print("\n" + "="*60 + "\n")

    try:
        clear_qdrant_collection()

        print("\n" + "="*60)
        print("✓ 数据清空完成")
        print("="*60 + "\n")

    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ 数据清空失败: {e}")
        print("="*60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
