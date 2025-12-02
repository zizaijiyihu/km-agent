"""
AIBase News 模块
用于获取 AIBase 每日新闻，支持 API 和爬虫两种方式
"""

from .news_service import get_aibase_news

__all__ = ['get_aibase_news']
