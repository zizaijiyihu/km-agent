#!/usr/bin/env python3
"""
会话管理模块测试

测试会话管理的各项功能
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from km_agent import KMAgent
from conversation_repository import (
    list_conversations,
    get_conversation,
    get_conversation_history,
)


def test_conversation_manager():
    """测试会话管理器"""
    print("="*60)
    print("测试 1: 会话管理器基本功能")
    print("="*60)
    
    # 创建启用历史记录的Agent
    print("\n1. 创建启用历史记录的Agent...")
    agent = KMAgent(
        verbose=True,
        owner="test_user@example.com",
        enable_history=True
    )
    
    conversation_id = agent.conversation_manager.get_conversation_id()
    print(f"✓ 会话ID: {conversation_id}")
    
    # 测试对话
    print("\n2. 测试对话...")
    response = agent.chat("你好，请介绍一下你自己")
    print(f"✓ Agent回复: {response['response'][:100]}...")
    
    # 检查数据库中的消息
    print("\n3. 检查数据库中的消息...")
    history = get_conversation_history(conversation_id)
    print(f"✓ 数据库中有 {len(history)} 条消息")
    
    for i, msg in enumerate(history, 1):
        print(f"  {i}. [{msg['role']}] {msg['content'][:50] if msg['content'] else 'N/A'}...")
    
    print("\n✓ 测试通过！")


def test_conversation_persistence():
    """测试会话持久化"""
    print("\n" + "="*60)
    print("测试 2: 会话持久化")
    print("="*60)
    
    owner = "test_user@example.com"
    
    # 第一次对话
    print("\n1. 创建第一个会话...")
    agent1 = KMAgent(
        verbose=False,
        owner=owner,
        enable_history=True
    )
    
    agent1.conversation_manager.update_title("测试会话 - 第一次对话")
    response1 = agent1.chat("我叫张三")
    conversation_id_1 = agent1.conversation_manager.get_conversation_id()
    print(f"✓ 会话1 ID: {conversation_id_1}")
    
    # 第二次对话(新会话)
    print("\n2. 创建第二个会话...")
    agent2 = KMAgent(
        verbose=False,
        owner=owner,
        enable_history=True
    )
    
    agent2.conversation_manager.update_title("测试会话 - 第二次对话")
    response2 = agent2.chat("我叫李四")
    conversation_id_2 = agent2.conversation_manager.get_conversation_id()
    print(f"✓ 会话2 ID: {conversation_id_2}")
    
    # 查询会话列表
    print("\n3. 查询会话列表...")
    conversations = list_conversations(owner, limit=10)
    print(f"✓ 找到 {len(conversations)} 个会话")
    
    for conv in conversations:
        print(f"  - {conv['title']} (ID: {conv['conversation_id'][:8]}...)")
    
    # 验证会话隔离
    print("\n4. 验证会话隔离...")
    history1 = get_conversation_history(conversation_id_1)
    history2 = get_conversation_history(conversation_id_2)
    
    print(f"✓ 会话1有 {len(history1)} 条消息")
    print(f"✓ 会话2有 {len(history2)} 条消息")
    
    # 检查内容是否正确隔离
    user_msg_1 = [m for m in history1 if m['role'] == 'user'][0]['content']
    user_msg_2 = [m for m in history2 if m['role'] == 'user'][0]['content']
    
    assert "张三" in user_msg_1, "会话1应该包含'张三'"
    assert "李四" in user_msg_2, "会话2应该包含'李四'"
    assert "张三" not in user_msg_2, "会话2不应该包含'张三'"
    
    print("✓ 会话隔离验证通过！")


def test_conversation_continuation():
    """测试会话续接"""
    print("\n" + "="*60)
    print("测试 3: 会话续接")
    print("="*60)
    
    owner = "test_user@example.com"
    
    # 创建会话并发送第一条消息
    print("\n1. 创建会话并发送第一条消息...")
    agent1 = KMAgent(
        verbose=False,
        owner=owner,
        enable_history=True
    )
    
    response1 = agent1.chat("我的名字是王五")
    conversation_id = agent1.conversation_manager.get_conversation_id()
    print(f"✓ 会话ID: {conversation_id}")
    print(f"✓ 第一次回复: {response1['response'][:50]}...")
    
    # 使用相同的conversation_id创建新的Agent实例
    print("\n2. 使用相同的conversation_id创建新Agent...")
    agent2 = KMAgent(
        verbose=False,
        owner=owner,
        conversation_id=conversation_id,
        enable_history=True
    )
    
    # 加载历史记录
    print("\n3. 加载历史记录...")
    history = agent2.conversation_manager.load_history()
    print(f"✓ 加载了 {len(history)} 条历史消息")
    
    # 继续对话
    print("\n4. 继续对话...")
    response2 = agent2.chat("你还记得我的名字吗?", history=history)
    print(f"✓ 第二次回复: {response2['response'][:100]}...")
    
    # 验证Agent是否记住了之前的对话
    if "王五" in response2['response']:
        print("✓ Agent成功记住了之前的对话内容！")
    else:
        print("⚠️  Agent可能没有记住之前的对话内容")
    
    # 检查数据库
    print("\n5. 检查数据库中的完整历史...")
    db_history = get_conversation_history(conversation_id)
    print(f"✓ 数据库中有 {len(db_history)} 条消息")
    
    user_messages = [m for m in db_history if m['role'] == 'user']
    print(f"✓ 用户消息数: {len(user_messages)}")
    for i, msg in enumerate(user_messages, 1):
        print(f"  {i}. {msg['content']}")


def test_streaming_with_history():
    """测试流式响应与历史记录"""
    print("\n" + "="*60)
    print("测试 4: 流式响应与历史记录")
    print("="*60)
    
    owner = "test_user@example.com"
    
    print("\n1. 创建启用历史的Agent...")
    agent = KMAgent(
        verbose=False,
        owner=owner,
        enable_history=True
    )
    
    conversation_id = agent.conversation_manager.get_conversation_id()
    print(f"✓ 会话ID: {conversation_id}")
    
    print("\n2. 使用流式响应发送消息...")
    collected_content = ""
    final_data = None
    
    for chunk in agent.chat_stream("请简单介绍一下Python语言"):
        if chunk['type'] == 'content':
            collected_content += chunk['data']
            print(chunk['data'], end='', flush=True)
        elif chunk['type'] == 'done':
            final_data = chunk['data']
    
    print(f"\n\n✓ 收到完整响应 ({len(collected_content)} 字符)")
    
    # 检查数据库
    print("\n3. 检查数据库中的消息...")
    history = get_conversation_history(conversation_id)
    print(f"✓ 数据库中有 {len(history)} 条消息")
    
    # 验证消息内容
    assistant_messages = [m for m in history if m['role'] == 'assistant']
    if assistant_messages:
        db_content = assistant_messages[-1]['content']
        if db_content == collected_content:
            print("✓ 数据库内容与流式响应一致！")
        else:
            print(f"⚠️  内容不一致: DB={len(db_content)} vs Stream={len(collected_content)}")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("会话管理模块测试套件")
    print("="*60)
    
    try:
        test_conversation_manager()
        test_conversation_persistence()
        test_conversation_continuation()
        test_streaming_with_history()
        
        print("\n" + "="*60)
        print("✓ 所有测试通过！")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
