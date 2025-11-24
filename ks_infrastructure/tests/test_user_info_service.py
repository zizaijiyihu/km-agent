#!/usr/bin/env python3
"""
测试用户信息服务功能

该脚本测试ks_infrastructure模块中的用户信息服务
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def test_user_info_service():
    """测试用户信息服务功能"""
    print("=== 测试用户信息服务功能 ===")
    try:
        from ks_infrastructure import ks_user_info

        # 获取用户信息服务
        user_info_service = ks_user_info()
        print("✓ 成功初始化用户信息服务")

        # 测试获取员工信息
        test_email_prefix = "lihaoze2"
        print(f"\n测试获取员工信息: {test_email_prefix}")

        # 方法1: 获取完整响应
        result = user_info_service.get_employee_info(test_email_prefix)

        if result.get('success'):
            data = result.get('data', {})
            print("✓ 成功获取员工信息:")
            print(f"  用户ID: {data.get('userId')}")
            print(f"  用户名: {data.get('userName')}")
            print(f"  工号: {data.get('userNo')}")
            print(f"  部门: {data.get('deptName')}")
            print(f"  完整部门路径: {data.get('deptFullName')}")
            print(f"  职位: {data.get('positionName')}")
            print(f"  职级: {data.get('rank')}")
            print(f"  地点: {data.get('location')}")
            print(f"  性别: {data.get('sex')}")
            print(f"  年龄: {data.get('age')}")
            print(f"  生日: {data.get('birthday')}")
            print(f"  学历: {data.get('education')}")
            print(f"  毕业院校: {data.get('graduationInstitution')}")
            print(f"  专业: {data.get('speciality')}")
            print(f"  入职日期: {data.get('joinedDate')}")
            print(f"  工龄: {data.get('workAge')}年")
            print(f"  合同到期: {data.get('contractExpire')}")
        else:
            print("✗ 获取员工信息失败")
            return False

        # 方法2: 直接获取数据部分
        print(f"\n测试快捷方法获取员工数据: {test_email_prefix}")
        employee_data = user_info_service.get_employee_data(test_email_prefix)

        if employee_data:
            print(f"✓ 成功获取员工数据: {employee_data.get('userName')} ({employee_data.get('userId')})")
            return True
        else:
            print("✗ 获取员工数据失败")
            return False

    except Exception as e:
        print(f"✗ 用户信息服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_user():
    """测试查询不存在的用户"""
    print("\n=== 测试查询不存在的用户 ===")
    try:
        from ks_infrastructure import ks_user_info

        # 获取用户信息服务
        user_info_service = ks_user_info()

        # 测试不存在的用户
        invalid_email_prefix = "nonexistentuser999"
        print(f"测试查询不存在的用户: {invalid_email_prefix}")

        try:
            result = user_info_service.get_employee_info(invalid_email_prefix)
            print(f"✗ 预期应该抛出异常，但返回了: {result}")
            return False
        except Exception as e:
            print(f"✓ 正确处理了不存在的用户，异常信息: {str(e)}")
            return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("开始测试用户信息服务功能...")
    print("=" * 50)

    test_results = {}

    # 测试正常查询
    test_results['正常查询用户'] = test_user_info_service()

    # 测试异常情况
    test_results['查询不存在的用户'] = test_invalid_user()

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
