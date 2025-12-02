"""
AIBase 新闻服务测试脚本
"""

import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aibase_news import get_aibase_news

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_api_fetch():
    """测试 API 获取新闻"""
    print("\n" + "=" * 80)
    print("测试 1: API 获取新闻 (4页)")
    print("=" * 80)

    try:
        news = get_aibase_news(pages=4, lang_type="zh_cn", use_crawler_fallback=False)

        if news:
            print(f"✅ API 成功获取 {len(news)} 条新闻")
            print("\n前 3 条新闻示例:")
            for i, item in enumerate(news[:3], 1):
                print(f"\n新闻 {i}:")
                print(f"  标题: {item.get('title', 'N/A')}")
                print(f"  描述: {item.get('description', 'N/A')[:100]}...")
                print(f"  链接: {item.get('url', 'N/A')}")
                print(f"  时间: {item.get('publishedTime', 'N/A')}")
            return True
        else:
            print("❌ API 未能获取到新闻")
            return False

    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crawler_fetch():
    """测试爬虫获取新闻"""
    print("\n" + "=" * 80)
    print("测试 2: 爬虫获取新闻 (最多15条)")
    print("=" * 80)

    try:
        # 直接使用爬虫方式
        import asyncio
        from aibase_news.news_service import fetch_news_from_crawler

        news = asyncio.run(fetch_news_from_crawler(max_news=15))

        if news:
            print(f"✅ 爬虫成功获取 {len(news)} 条新闻")
            print("\n前 3 条新闻示例:")
            for i, item in enumerate(news[:3], 1):
                print(f"\n新闻 {i}:")
                print(f"  标题: {item.get('title', 'N/A')}")
                print(f"  描述: {item.get('description', 'N/A')[:100]}...")
                print(f"  链接: {item.get('url', 'N/A')}")
                print(f"  时间: {item.get('publishedTime', 'N/A')}")
            return True
        else:
            print("❌ 爬虫未能获取到新闻")
            return False

    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_fallback():
    """测试自动降级功能"""
    print("\n" + "=" * 80)
    print("测试 3: 自动降级 (API -> 爬虫)")
    print("=" * 80)

    try:
        news = get_aibase_news(pages=4, use_crawler_fallback=True)

        if news:
            print(f"✅ 成功获取 {len(news)} 条新闻 (可能来自 API 或爬虫)")
            print("\n前 3 条新闻示例:")
            for i, item in enumerate(news[:3], 1):
                print(f"\n新闻 {i}:")
                print(f"  标题: {item.get('title', 'N/A')}")
                print(f"  描述: {item.get('description', 'N/A')[:100]}...")
            return True
        else:
            print("❌ 未能获取到新闻")
            return False

    except Exception as e:
        print(f"❌ 自动降级测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("AIBase 新闻服务自动测试")
    print("=" * 80)

    results = {
        "API 获取": False,
        "爬虫获取": False,
        "自动降级": False
    }

    # 测试 1: API 获取
    results["API 获取"] = test_api_fetch()

    # 测试 2: 爬虫获取 (如果 API 失败才测试)
    if not results["API 获取"]:
        print("\n⚠️  API 测试失败，将测试爬虫方式...")
        results["爬虫获取"] = test_crawler_fetch()

    # 测试 3: 自动降级
    results["自动降级"] = test_auto_fallback()

    # 输出测试总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    # 判断整体是否通过
    if results["自动降级"]:
        print("\n🎉 整体测试通过！至少有一种方式可以获取新闻。")
        return 0
    else:
        print("\n❌ 整体测试失败！所有方式都无法获取新闻。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
