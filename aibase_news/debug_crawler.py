"""
调试爬虫获取的内容
"""

import asyncio
from crawl4ai import AsyncWebCrawler
import json


async def debug_fetch():
    """调试抓取网页内容"""
    url = "https://news.aibase.com/zh/daily"

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url, bypass_cache=True)

        if result.success:
            print("\n" + "=" * 80)
            print("HTML 长度:", len(result.html))
            print("Markdown 长度:", len(result.markdown))
            print("\n" + "=" * 80)
            print("Markdown 内容前 2000 字符:")
            print(result.markdown[:2000])

            # 保存到文件
            with open("/tmp/aibase_page.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            with open("/tmp/aibase_page.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)

            print("\n" + "=" * 80)
            print("✅ 已保存到:")
            print("  HTML: /tmp/aibase_page.html")
            print("  Markdown: /tmp/aibase_page.md")
        else:
            print(f"❌ 爬取失败: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(debug_fetch())
