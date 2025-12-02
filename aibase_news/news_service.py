"""
AIBase 新闻获取服务
支持 API 和爬虫两种方式获取新闻
"""

import logging
import time
import requests
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler
import asyncio

logger = logging.getLogger(__name__)


def fetch_news_from_api(pages: int = 4, lang_type: str = "zh_cn") -> Optional[List[Dict]]:
    """
    从 API 获取新闻

    Args:
        pages: 要获取的页数，默认 4 页
        lang_type: 语言类型，默认 "zh_cn"（简体中文）。可选值：zh_cn, en, ja 等

    Returns:
        新闻列表，如果失败返回 None
    """
    try:
        all_news = []

        for page_no in range(1, pages + 1):
            timestamp = int(time.time() * 1000)
            url = f"https://mcpapi.aibase.cn/api/aiInfo/dailyNews?t={timestamp}&langType={lang_type}&pageNo={page_no}"

            logger.info(f"正在获取第 {page_no} 页新闻: {url}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 检查响应状态
            if data.get('code') != 200:
                logger.error(f"API 返回错误: {data.get('message', '未知错误')}")
                return None

            # 提取新闻数据
            news_list = data.get('data', {}).get('list', [])
            if not news_list:
                logger.warning(f"第 {page_no} 页没有新闻数据")
                break

            # 转换为统一格式
            for item in news_list:
                all_news.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': f"https://news.aibase.com/zh/daily/{item.get('oid', '')}" if item.get('oid') else '',
                    'publishedTime': item.get('createTime', '')
                })

            logger.info(f"成功获取第 {page_no} 页 {len(news_list)} 条新闻")

            # 避免请求过快
            if page_no < pages:
                time.sleep(0.5)

        logger.info(f"API 总共获取 {len(all_news)} 条新闻")
        return all_news

    except requests.exceptions.RequestException as e:
        logger.error(f"API 请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"API 获取新闻时发生错误: {e}")
        return None


async def fetch_news_from_crawler(url: str = "https://news.aibase.com/zh/daily", max_news: int = 15) -> Optional[List[Dict]]:
    """
    使用 Crawl4AI 爬取新闻（兜底方案）

    Args:
        url: 要爬取的网页 URL
        max_news: 最多获取的新闻数量，默认 15 条

    Returns:
        新闻列表，如果失败返回 None
    """
    try:
        logger.info(f"使用 Crawl4AI 爬取新闻: {url}")

        # 导入 OpenAI 服务
        from ks_infrastructure.services.openai_service import ks_openai

        # 获取 OpenAI 客户端
        openai_client = ks_openai()

        # 先尝试使用 LLM 直接提取（最可靠）
        return await fetch_news_with_llm(url, max_news, openai_client)

    except Exception as e:
        logger.error(f"爬取新闻时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None


async def fetch_news_with_llm(url: str, max_news: int, openai_client) -> Optional[List[Dict]]:
    """
    使用 LLM 提取新闻
    """
    try:
        logger.info("使用 LLM 方式提取新闻...")

        # 简单爬取网页内容
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, bypass_cache=True)

            if not result.success:
                logger.error(f"LLM 方式爬取失败: {result.error_message}")
                return None

            # 使用 Markdown 内容，更易于 LLM 理解
            markdown_content = result.markdown[:15000]  # 提高限制到 15000

            prompt = f"""
请从下面的网页 Markdown 内容中提取 AI 相关的每日新闻条目。

提取要求：
1. 找到所有带有新闻标题的条目（通常在"最新AI日报"或"AI日报"部分）
2. 最多提取 {max_news} 条新闻
3. 每条新闻需包含：标题、简短描述、链接（如果有）
4. 以 JSON 数组格式输出，每个对象包含：title（标题）、description（描述）、url（链接，完整URL）、published_time（发布时间，如果有）

网页内容：
{markdown_content}

请严格按照 JSON 格式返回，不要包含任何其他文字说明。直接输出 JSON 数组。
"""

            # 获取配置的模型
            from ks_infrastructure.configs.default import OPENAI_CONFIG
            model_name = OPENAI_CONFIG.get("model", "DeepSeek-V3.1-Ksyun")

            logger.info(f"使用模型 {model_name} 提取新闻...")

            response = openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的网页内容提取助手。你需要从给定的网页内容中提取结构化的新闻信息，并以严格的 JSON 格式返回。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            import json
            import re

            content = response.choices[0].message.content.strip()
            logger.debug(f"LLM 返回内容: {content[:500]}...")

            # 尝试多种方式提取 JSON
            # 1. 直接解析
            try:
                news_data = json.loads(content)
            except:
                # 2. 提取 ```json 代码块
                json_block = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if json_block:
                    news_data = json.loads(json_block.group(1))
                else:
                    # 3. 提取 [...] 部分
                    json_match = re.search(r'(\[.*\])', content, re.DOTALL)
                    if json_match:
                        news_data = json.loads(json_match.group(1))
                    else:
                        logger.error("LLM 返回的内容不包含有效的 JSON")
                        logger.debug(f"完整内容: {content}")
                        return None

            # 转换为统一格式
            news_list = []
            for item in news_data[:max_news]:
                if isinstance(item, dict) and item.get('title'):
                    # 确保 URL 是完整的
                    item_url = (item.get('url') or '').strip()
                    if item_url and not item_url.startswith('http'):
                        item_url = f"https://news.aibase.com{item_url}" if item_url.startswith('/') else item_url

                    news_list.append({
                        'title': (item.get('title') or '').strip(),
                        'description': (item.get('description') or '').strip(),
                        'url': item_url,
                        'publishedTime': (item.get('published_time') or '').strip()
                    })

            if news_list:
                logger.info(f"LLM 成功提取 {len(news_list)} 条新闻")
                return news_list
            else:
                logger.warning("LLM 提取到的新闻列表为空")
                return None

    except Exception as e:
        logger.error(f"LLM 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_aibase_news(pages: int = 4, lang_type: str = "zh_cn", use_crawler_fallback: bool = True) -> List[Dict]:
    """
    获取 AIBase 每日新闻
    优先使用 API，如果失败则使用爬虫兜底

    Args:
        pages: API 要获取的页数，默认 4 页
        lang_type: 语言类型，默认 "zh_cn"（简体中文）。可选值：zh_cn, en, ja 等
        use_crawler_fallback: 是否使用爬虫作为兜底，默认 True

    Returns:
        新闻列表
    """
    # 首先尝试使用 API
    logger.info("尝试使用 API 获取新闻...")
    news = fetch_news_from_api(pages=pages, lang_type=lang_type)

    if news and len(news) > 0:
        logger.info(f"API 成功获取 {len(news)} 条新闻")
        return news

    # API 失败，使用爬虫兜底
    if use_crawler_fallback:
        logger.warning("API 获取失败，使用爬虫兜底...")
        try:
            # 运行异步爬虫
            news = asyncio.run(fetch_news_from_crawler())
            if news and len(news) > 0:
                logger.info(f"爬虫成功获取 {len(news)} 条新闻")
                return news
        except Exception as e:
            logger.error(f"爬虫兜底也失败了: {e}")

    logger.error("所有方法都失败了，返回空列表")
    return []
