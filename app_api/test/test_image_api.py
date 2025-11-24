#!/usr/bin/env python3
"""
测试图片上传并解析 API

测试 /api/analyze-image 端点
"""

import os
import sys
import requests

# API 配置
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')


def test_analyze_image():
    """测试图片上传并解析"""
    print("=" * 60)
    print("测试: 图片上传并解析")
    print("=" * 60)

    # 获取测试图片路径
    test_image_path = os.path.join(os.path.dirname(__file__), 'image.png')

    if not os.path.exists(test_image_path):
        print(f"✗ 测试图片不存在: {test_image_path}")
        return False

    print(f"测试图片: {test_image_path}")
    print(f"图片大小: {os.path.getsize(test_image_path)} bytes")

    # 测试1: 使用默认提示词
    print("\n--- 测试1: 使用默认提示词 ---")
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('image.png', f, 'image/png')}
            data = {'username': 'test_api_user'}

            response = requests.post(
                f"{API_BASE_URL}/api/analyze-image",
                files=files,
                data=data,
                timeout=60
            )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            if result.get('success'):
                print("✓ 图片分析成功")
                print(f"  图片URL: {result.get('image_url')}")
                print(f"  分析结果:\n{result.get('analysis')}\n")
            else:
                print(f"✗ 图片分析失败: {result.get('error')}")
                return False
        else:
            print(f"✗ API 请求失败: {response.text}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试2: 使用自定义提示词
    print("\n--- 测试2: 使用自定义提示词 ---")
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('custom_image.png', f, 'image/png')}
            data = {
                'username': 'test_api_user',
                'prompt': '请识别这张图片中的所有文字内容，并按照原始结构输出。'
            }

            response = requests.post(
                f"{API_BASE_URL}/api/analyze-image",
                files=files,
                data=data,
                timeout=60
            )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            if result.get('success'):
                print("✓ 自定义提示词分析成功")
                print(f"  图片URL: {result.get('image_url')}")
                print(f"  分析结果:\n{result.get('analysis')}\n")
                return True
            else:
                print(f"✗ 自定义提示词分析失败: {result.get('error')}")
                return False
        else:
            print(f"✗ API 请求失败: {response.text}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_file_type():
    """测试无效文件类型"""
    print("\n" + "=" * 60)
    print("测试: 无效文件类型")
    print("=" * 60)

    try:
        # 创建一个假的 txt 文件
        files = {'file': ('test.txt', b'This is a text file', 'text/plain')}
        data = {'username': 'test_user'}

        response = requests.post(
            f"{API_BASE_URL}/api/analyze-image",
            files=files,
            data=data,
            timeout=10
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 400:
            result = response.json()
            if not result.get('success') and 'Invalid file type' in result.get('error', ''):
                print("✓ 正确拒绝了无效文件类型")
                print(f"  错误信息: {result.get('error')}")
                return True
            else:
                print(f"✗ 错误处理不符合预期: {result}")
                return False
        else:
            print(f"✗ 期望状态码 400，实际: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_missing_file():
    """测试缺少文件"""
    print("\n" + "=" * 60)
    print("测试: 缺少文件参数")
    print("=" * 60)

    try:
        data = {'username': 'test_user'}

        response = requests.post(
            f"{API_BASE_URL}/api/analyze-image",
            data=data,
            timeout=10
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 400:
            result = response.json()
            if not result.get('success') and 'No file provided' in result.get('error', ''):
                print("✓ 正确处理了缺少文件的情况")
                print(f"  错误信息: {result.get('error')}")
                return True
            else:
                print(f"✗ 错误处理不符合预期: {result}")
                return False
        else:
            print(f"✗ 期望状态码 400，实际: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n开始测试图片分析 API...")
    print(f"API 地址: {API_BASE_URL}")
    print("=" * 60)

    # 先检查 API 是否可用
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ API 服务正常")
        else:
            print(f"✗ API 服务异常: {response.status_code}")
            print("请先启动 API 服务: python -m app_api.api")
            return 1
    except Exception as e:
        print(f"✗ 无法连接到 API 服务: {e}")
        print("请先启动 API 服务: python -m app_api.api")
        return 1

    test_results = {}

    # 运行测试
    test_results['图片上传并解析'] = test_analyze_image()
    test_results['无效文件类型'] = test_invalid_file_type()
    test_results['缺少文件参数'] = test_missing_file()

    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:>20}: {status}")
        if result:
            passed_tests += 1

    print("-" * 60)
    print(f"总计: {passed_tests}/{total_tests} 项测试通过")

    if passed_tests == total_tests:
        print("\n🎉 所有测试均通过!")
        return 0
    else:
        print(f"\n⚠ {total_tests - passed_tests} 项测试失败，请检查相关配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
