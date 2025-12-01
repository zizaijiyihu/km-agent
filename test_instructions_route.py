#!/usr/bin/env python3
"""
测试 instructions 路由
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_api.api import create_app

def test_instructions_route():
    """测试 GET /api/instructions"""
    app = create_app()

    with app.test_client() as client:
        print("Testing GET /api/instructions...")
        try:
            response = client.get('/api/instructions')
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.get_json()}")

            if response.status_code == 200:
                print("✓ 测试成功")
            else:
                print("✗ 测试失败")

        except Exception as e:
            print(f"✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_instructions_route()
