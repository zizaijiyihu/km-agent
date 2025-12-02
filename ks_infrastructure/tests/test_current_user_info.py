#!/usr/bin/env python3
"""
测试 get_current_user_info 方法
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ks_infrastructure.services.user_info_service import ks_user_info, get_current_user

def test_get_current_user_info():
    """测试获取当前用户信息"""
    print("=" * 80)
    print("测试 get_current_user_info 方法")
    print("=" * 80)
    
    # 创建服务实例
    service = ks_user_info()
    
    # 测试1: 不传参数，使用默认当前用户
    print("\n测试1: 获取默认当前用户信息")
    print("-" * 80)
    try:
        result = service.get_current_user_info()
        print(f"✅ 成功获取用户信息")
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            data = result.get('data', {})
            print(f"   用户ID: {data.get('userId')}")
            print(f"   用户名: {data.get('userName')}")
            print(f"   工号: {data.get('userNo')}")
            print(f"   部门: {data.get('deptName')}")
            print(f"   职位: {data.get('positionName')}")
            print(f"   职级: {data.get('rank')}")
            print(f"   工作地点: {data.get('location')}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试2: 显式传入当前用户
    print("\n测试2: 显式传入当前用户邮箱前缀")
    print("-" * 80)
    current_user = get_current_user()
    print(f"   当前用户: {current_user}")
    try:
        result = service.get_current_user_info(current_user_email_prefix=current_user)
        print(f"✅ 成功获取用户信息")
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            data = result.get('data', {})
            print(f"   用户名: {data.get('userName')}")
            print(f"   部门全称: {data.get('deptFullName')}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试3: 传入其他用户（如果存在）
    print("\n测试3: 传入其他用户邮箱前缀")
    print("-" * 80)
    other_user = "lihaoze2"  # 假设这是一个存在的用户
    print(f"   目标用户: {other_user}")
    try:
        result = service.get_current_user_info(current_user_email_prefix=other_user)
        print(f"✅ 成功获取用户信息")
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            data = result.get('data', {})
            print(f"   用户名: {data.get('userName')}")
            print(f"   部门: {data.get('deptName')}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_get_current_user_info()
