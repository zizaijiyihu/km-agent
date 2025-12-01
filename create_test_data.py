
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from conversation_repository.db import create_conversation, add_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    owner = "huxiaoxiao"
    
    # Conversation 1: Python Basics
    conv1_id = create_conversation(owner, "Python 基础知识")
    add_message(conv1_id, "user", "Python 中的列表推导式怎么写？")
    add_message(conv1_id, "assistant", "Python 列表推导式是一种简洁的创建列表的方法。\n\n基本语法：\n```python\n[expression for item in iterable if condition]\n```\n\n例如，生成 0-9 的平方列表：\n```python\nsquares = [x**2 for x in range(10)]\nprint(squares)\n# Output: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\n```")
    add_message(conv1_id, "user", "那字典推导式呢？")
    add_message(conv1_id, "assistant", "字典推导式也很类似，只是使用花括号 `{}` 并指定键值对。\n\n语法：\n```python\n{key_expression: value_expression for item in iterable if condition}\n```\n\n例如：\n```python\nsquares_dict = {x: x**2 for x in range(5)}\nprint(squares_dict)\n# Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}\n```")
    logger.info(f"Created conversation 1: {conv1_id}")

    # Conversation 2: Project Planning
    conv2_id = create_conversation(owner, "项目规划讨论")
    add_message(conv2_id, "user", "我们需要为新的 CRM 系统制定一个开发计划。")
    add_message(conv2_id, "assistant", "好的，制定 CRM 系统开发计划通常需要考虑以下几个阶段：\n\n1. **需求分析**：确定核心功能（客户管理、销售漏斗、报表等）。\n2. **技术选型**：前端（React/Vue）、后端（Python/Java/Node）、数据库（PostgreSQL/MySQL）。\n3. **原型设计**：UI/UX 设计。\n4. **开发迭代**：分模块开发。\n5. **测试与部署**。\n\n你想先从哪个方面开始讨论？")
    add_message(conv2_id, "user", "先聊聊技术选型吧，我们团队熟悉 Python。")
    add_message(conv2_id, "assistant", "既然团队熟悉 Python，后端框架推荐使用 **FastAPI** 或 **Django**。\n\n- **FastAPI**：性能高，原生支持异步，适合构建 RESTful API，灵活性强。\n- **Django**：功能全（自带 Admin、ORM），开发速度快，适合快速构建复杂应用。\n\n如果需要快速上线且业务逻辑复杂，Django 是不错的选择；如果追求高性能和微服务架构，FastAPI 更合适。")
    logger.info(f"Created conversation 2: {conv2_id}")

    # Conversation 3: Daily Chat
    conv3_id = create_conversation(owner, "日常闲聊")
    add_message(conv3_id, "user", "今天天气真不错。")
    add_message(conv3_id, "assistant", "是啊，天气好心情也会变好！你打算去哪里玩吗？")
    logger.info(f"Created conversation 3: {conv3_id}")
    
    # Conversation 4: Empty Conversation
    conv4_id = create_conversation(owner, "新会话")
    logger.info(f"Created conversation 4: {conv4_id}")

    print("\nSuccessfully created test conversations for user 'huxiaoxiao'!")

if __name__ == "__main__":
    create_test_data()
