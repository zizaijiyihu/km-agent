#!/usr/bin/env python3
"""
测试图片分析模块

测试图片上传到临时桶和视觉识别解析功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def test_analyze_image():
    """测试单张图片分析"""
    print("=== 测试图片分析功能 ===")
    try:
        from tmp_image_repository import analyze_temp_image

        # 获取测试图片路径
        test_image_path = os.path.join(os.path.dirname(__file__), 'image.png')

        if not os.path.exists(test_image_path):
            print(f"✗ 测试图片不存在: {test_image_path}")
            return False

        print(f"测试图片: {test_image_path}")

        # 测试默认提示词
        print("\n--- 测试1: 使用默认提示词 ---")
        result = analyze_temp_image(
            image_path=test_image_path,
            username='test_user'
        )

        if result['success']:
            print("✓ 图片分析成功")
            print(f"  图片URL: {result['image_url']}")
            print(f"  分析结果:\n{result['analysis']}\n")
        else:
            print(f"✗ 图片分析失败: {result.get('error')}")
            return False

        # 测试自定义提示词
        print("\n--- 测试2: 使用自定义提示词 ---")
        custom_prompt = "请识别这张图片中的文字内容，如果有的话。"
        result2 = analyze_temp_image(
            image_path=test_image_path,
            username='test_user',
            prompt=custom_prompt,
            custom_filename='custom_test.png'
        )

        if result2['success']:
            print("✓ 自定义提示词分析成功")
            print(f"  图片URL: {result2['image_url']}")
            print(f"  分析结果:\n{result2['analysis']}\n")
            return True
        else:
            print(f"✗ 自定义提示词分析失败: {result2.get('error')}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_analyze():
    """测试批量图片分析"""
    print("\n=== 测试批量图片分析功能 ===")
    try:
        from tmp_image_repository import batch_analyze_images

        # 获取测试图片路径（这里用同一张图片测试）
        test_image_path = os.path.join(os.path.dirname(__file__), 'image.png')

        if not os.path.exists(test_image_path):
            print(f"✗ 测试图片不存在: {test_image_path}")
            return False

        # 批量分析（用同一张图片模拟多张）
        image_paths = [test_image_path]
        print(f"批量分析 {len(image_paths)} 张图片")

        results = batch_analyze_images(
            image_paths=image_paths,
            username='batch_test_user'
        )

        success_count = sum(1 for r in results if r['success'])
        print(f"✓ 批量分析完成: {success_count}/{len(results)} 张成功")

        for i, result in enumerate(results, 1):
            if result['success']:
                print(f"\n图片 {i}:")
                print(f"  URL: {result['image_url']}")
                print(f"  分析: {result['analysis'][:100]}...")
            else:
                print(f"\n图片 {i}: 失败 - {result.get('error')}")

        return success_count == len(results)

    except Exception as e:
        print(f"✗ 批量测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    try:
        from tmp_image_repository import analyze_temp_image

        # 测试不存在的文件
        print("测试不存在的文件...")
        result = analyze_temp_image(
            image_path='/nonexistent/path/image.png',
            username='test_user'
        )

        if not result['success'] and 'error' in result:
            print(f"✓ 正确处理文件不存在错误: {result['error']}")
            return True
        else:
            print("✗ 错误处理异常")
            return False

    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始测试图片分析模块...")
    print("=" * 50)

    test_results = {}

    # 测试单张图片分析
    test_results['单张图片分析'] = test_analyze_image()

    # 测试批量分析
    test_results['批量图片分析'] = test_batch_analyze()

    # 测试错误处理
    test_results['错误处理'] = test_error_handling()

    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:>15}: {status}")
        if result:
            passed_tests += 1

    print("-" * 50)
    print(f"总计: {passed_tests}/{total_tests} 项测试通过")

    if passed_tests == total_tests:
        print("\n🎉 所有测试均通过!")
        return 0
    else:
        print(f"\n⚠ {total_tests - passed_tests} 项测试失败，请检查相关配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
