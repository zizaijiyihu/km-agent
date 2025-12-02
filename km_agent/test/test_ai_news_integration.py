#!/usr/bin/env python3
"""
测试 AI 新闻工具的完整集成
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from km_agent.agent import KMAgent

def test_ai_news_query():
    """测试通过 Agent 查询 AI 新闻"""
    print("=" * 80)
    print("测试 AI 新闻查询功能")
    print("=" * 80)
    
    # 创建 Agent 实例（不启用历史记录）
    agent = KMAgent(verbose=True, enable_history=False)
    
    # 测试查询
    test_queries = [
        "最近有什么AI新闻？",
        "给我看看最新的5条AI资讯",
        "有什么AI相关的最新消息吗？"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}: {query}")
        print(f"{'='*80}\n")
        
        print("Agent 回复: ", end="", flush=True)
        
        # 使用流式响应
        for chunk in agent.chat_stream(query, history=None):
            if chunk["type"] == "content":
                print(chunk["data"], end="", flush=True)
            elif chunk["type"] == "tool_call":
                print(f"\n[调用工具: {chunk['data']['tool']}]", flush=True)
            elif chunk["type"] == "done":
                print("\n\n[完成]")
                if chunk["data"]["tool_calls"]:
                    print(f"总共调用了 {len(chunk['data']['tool_calls'])} 个工具")
        
        print("\n" + "="*80)
        
        # 只测试第一个查询
        break

if __name__ == "__main__":
    test_ai_news_query()
