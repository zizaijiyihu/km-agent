# AIBase News 模块

用于获取 [AIBase](https://news.aibase.com/zh/daily) 每日 AI 新闻的独立模块。

## 功能特性

- 📡 **双重获取策略**：优先使用 API，失败时自动切换到爬虫
- 🔄 **自动降级**：API 不可用时自动使用 Crawl4AI 爬虫兜底
- 📰 **批量获取**：支持获取多页新闻（API 方式）
- 🛡️ **容错机制**：完善的错误处理和日志记录

## 安装依赖

```bash
pip install requests crawl4ai pydantic
```

## 使用方法

### 基本用法

```python
from aibase_news import get_aibase_news

# 获取新闻（默认 4 页，自动降级）
news = get_aibase_news()

# 打印新闻
for item in news:
    print(f"标题: {item['title']}")
    print(f"描述: {item['description']}")
    print(f"链接: {item['url']}")
    print(f"时间: {item['publishedTime']}")
    print("-" * 80)
```

### 高级用法

```python
# 自定义页数
news = get_aibase_news(pages=2)

# 指定语言（zh_cn=简体中文, en=英文, ja=日文等）
news = get_aibase_news(lang_type="en")

# 禁用爬虫兜底（仅使用 API）
news = get_aibase_news(use_crawler_fallback=False)
```

### 单独使用 API 方式

```python
from aibase_news.news_service import fetch_news_from_api

# 注意：lang_type 必须使用 "zh_cn" 而不是 "zh"
news = fetch_news_from_api(pages=4, lang_type="zh_cn")
if news:
    print(f"获取到 {len(news)} 条新闻")
```

### 单独使用爬虫方式

```python
import asyncio
from aibase_news.news_service import fetch_news_from_crawler

news = asyncio.run(fetch_news_from_crawler(max_news=15))
if news:
    print(f"获取到 {len(news)} 条新闻")
```

## 运行测试

```bash
cd /Users/xiaohu/projects/km-agent_2
python aibase_news/test_news_service.py
```

测试脚本会依次测试：
1. API 获取新闻
2. 爬虫获取新闻（如果 API 失败）
3. 自动降级功能

## 数据格式

返回的新闻列表中，每条新闻包含以下字段：

```python
{
    "title": "新闻标题",
    "description": "新闻描述/摘要",
    "url": "新闻链接",
    "publishedTime": "发布时间"
}
```

## 工作原理

1. **API 方式**：
   - 调用 `https://mcpapi.aibase.cn/api/aiInfo/dailyNews` 接口
   - 支持分页获取，默认获取 4 页
   - 每页之间间隔 0.5 秒，避免请求过快

2. **爬虫方式**（兜底）：
   - 使用 Crawl4AI 爬取 `https://news.aibase.com/zh/daily`
   - 使用 OpenAI GPT-4o-mini 提取结构化数据
   - 最多提取 15 条新闻

3. **自动切换逻辑**：
   - 优先尝试 API 方式
   - API 失败或返回空数据时，自动切换到爬虫方式
   - 可通过参数禁用自动降级

## 依赖服务

- **OpenAI 服务**：爬虫方式需要使用 `ks_infrastructure.services.openai_service`
- **网络连接**：需要能访问 aibase.com 域名

## 日志

模块使用 Python 标准日志库，默认记录：
- 每次请求的状态
- 获取的新闻数量
- 错误和异常信息

可通过配置日志级别控制输出详细程度：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 注意事项

1. **重要**：API 的 `lang_type` 参数必须使用 `zh_cn`（而不是 `zh`）才能获取简体中文新闻
2. API 接口可能会有访问限制或变更，爬虫方式作为可靠的兜底方案
3. 爬虫方式需要消耗 LLM API 调用（约 1-2 分钟/次），请注意成本
4. 建议生产环境启用日志监控，及时发现 API 失效情况
5. API 方式速度快（约 2 秒获取 32 条新闻），爬虫方式速度较慢

## 版本历史

- **v1.0.0** (2025-12-02)
  - 初始版本
  - 支持 API 和爬虫双重获取策略
  - 自动降级机制
  - 完整的测试套件
