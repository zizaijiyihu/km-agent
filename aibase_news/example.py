"""
AIBase 新闻模块使用示例
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aibase_news import get_aibase_news


def main():
    """演示如何使用 aibase_news 模块"""

    print("=" * 80)
    print("AIBase 新闻获取示例")
    print("=" * 80)

    # 获取新闻（默认参数）
    print("\n正在获取 AIBase 每日新闻...")
    news_list = get_aibase_news()

    if news_list:
        print(f"\n✅ 成功获取 {len(news_list)} 条新闻\n")

        # 显示前 5 条
        for i, news in enumerate(news_list[:5], 1):
            print(f"新闻 {i}:")
            print(f"  标题: {news['title']}")
            print(f"  描述: {news['description'][:150]}..." if len(news['description']) > 150 else f"  描述: {news['description']}")
            print(f"  链接: {news['url']}")
            if news['publishedTime']:
                print(f"  时间: {news['publishedTime']}")
            print()

        # 演示其他用法
        print("\n" + "=" * 80)
        print("其他用法示例:")
        print("=" * 80)
        print("""
# 1. 仅使用 API（不启用爬虫兜底）
news = get_aibase_news(pages=2, use_crawler_fallback=False)

# 2. 获取更多页（API 方式）
news = get_aibase_news(pages=6)

# 3. 获取英文新闻（如果 API 支持）
news = get_aibase_news(lang_type="en")

# 4. 在代码中使用
for item in news:
    title = item['title']
    description = item['description']
    url = item['url']
    # 进行进一步处理...
        """)
    else:
        print("❌ 未能获取到新闻")


if __name__ == "__main__":
    main()
