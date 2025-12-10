#!/usr/bin/env python3
"""
Vision服务测试脚本 - 使用真实图片
测试金山云Vision服务的连接性和图像分析功能
"""

import sys
import os
import base64
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ks_infrastructure.services.vision_service import ks_vision
from ks_infrastructure.services.exceptions import KsServiceError, KsConfigError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_image_from_file(image_path: str) -> tuple[str, str]:
    """
    从文件加载图像并转换为base64
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        tuple: (base64_encoded_image, image_format)
    """
    try:
        # 获取文件扩展名
        _, ext = os.path.splitext(image_path)
        image_format = ext.lstrip('.').lower()
        
        # 读取图片文件
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # 转换为base64
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        logger.info(f"✓ 成功加载图片: {os.path.basename(image_path)}")
        logger.info(f"  - 格式: {image_format}")
        logger.info(f"  - 大小: {len(image_bytes) / 1024:.2f} KB")
        logger.info(f"  - Base64长度: {len(img_base64)} 字符")
        
        return img_base64, image_format
        
    except FileNotFoundError:
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    except Exception as e:
        raise Exception(f"加载图片失败: {e}")


def test_vision_service_connection():
    """测试Vision服务连接"""
    print("=" * 80)
    print("测试 Vision 服务连接")
    print("=" * 80)
    
    try:
        # 获取Vision服务实例
        logger.info("正在初始化 Vision 服务...")
        vision = ks_vision()
        
        logger.info(f"✓ Vision 服务初始化成功")
        logger.info(f"  - API Base URL: {vision.base_url}")
        logger.info(f"  - Model: {vision.model}")
        logger.info(f"  - API Key: {'***' + vision.api_key[-8:] if vision.api_key else 'None'}")
        
        return True, vision
        
    except Exception as e:
        logger.error(f"✗ Vision 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_vision_image_analysis(vision, image_path: str):
    """测试图像分析功能"""
    print("\n" + "=" * 80)
    print("测试图像分析功能")
    print("=" * 80)
    
    try:
        # 加载图像
        logger.info(f"正在加载图片: {image_path}")
        image_base64, image_format = load_image_from_file(image_path)
        
        # 测试图像分析
        logger.info("正在调用 Vision API 分析图像...")
        test_prompt = "请详细描述这张图片的内容，包括界面元素、文字、颜色和布局。"
        
        result = vision.analyze_image(
            image_base64=image_base64,
            image_format=image_format,
            prompt=test_prompt
        )
        
        logger.info(f"✓ 图像分析成功")
        logger.info(f"\n{'=' * 80}")
        logger.info(f"分析结果:")
        logger.info(f"{'=' * 80}")
        logger.info(f"{result}")
        logger.info(f"{'=' * 80}")
        
        return True, result
        
    except FileNotFoundError as e:
        logger.error(f"✗ {e}")
        return False, None
    
    except KsConfigError as e:
        logger.error(f"✗ 配置错误: {e}")
        return False, None
    
    except KsServiceError as e:
        logger.error(f"✗ 服务调用失败: {e}")
        return False, None
    
    except Exception as e:
        logger.error(f"✗ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_vision_with_custom_prompts(vision, image_path: str):
    """测试多个自定义提示词"""
    print("\n" + "=" * 80)
    print("测试多个自定义提示词")
    print("=" * 80)
    
    try:
        # 加载图像
        logger.info(f"正在加载图片: {image_path}")
        image_base64, image_format = load_image_from_file(image_path)
        
        # 使用不同的提示词
        custom_prompts = [
            "这张图片中有哪些主要的界面元素？",
            "请列出图片中所有可见的文字内容。",
            "这个界面的主要功能是什么？",
        ]
        
        for i, prompt in enumerate(custom_prompts, 1):
            logger.info(f"\n{'─' * 80}")
            logger.info(f"测试 {i}: {prompt}")
            logger.info(f"{'─' * 80}")
            
            result = vision.analyze_image(
                image_base64=image_base64,
                image_format=image_format,
                prompt=prompt
            )
            
            logger.info(f"✓ 回答:")
            logger.info(f"{result}\n")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 自定义提示词测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_report(results: dict, image_path: str) -> str:
    """生成测试报告"""
    report = []
    report.append("=" * 80)
    report.append("Vision服务测试报告（真实图片）")
    report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"测试图片: {os.path.basename(image_path)}")
    report.append("=" * 80)
    report.append("")
    
    # 测试结果统计
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v.get('success', False))
    
    report.append(f"总计: {total_tests} 个测试")
    report.append(f"通过: {passed_tests} 个")
    report.append(f"失败: {total_tests - passed_tests} 个")
    report.append("")
    
    # 详细结果
    for test_name, test_result in results.items():
        report.append("-" * 80)
        report.append(f"测试: {test_name}")
        report.append(f"状态: {'✓ 通过' if test_result.get('success') else '✗ 失败'}")
        
        if test_result.get('error'):
            report.append(f"错误: {test_result['error']}")
        
        if test_result.get('details'):
            report.append(f"详情: {test_result['details']}")
        
        if test_result.get('result'):
            report.append(f"\n分析结果:")
            report.append(f"{test_result['result']}")
        
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """主函数"""
    # 图片路径
    image_path = os.path.join(
        os.path.dirname(__file__),
        "Capture20251117-151125.png"
    )
    
    print("开始测试 Vision 服务（使用真实图片）...")
    print(f"测试图片: {image_path}")
    print("")
    
    # 检查图片是否存在
    if not os.path.exists(image_path):
        logger.error(f"图片文件不存在: {image_path}")
        return 1
    
    results = {}
    
    # 测试1: 连接测试
    success, vision = test_vision_service_connection()
    results['服务连接'] = {
        'success': success,
        'details': f"Base URL: {vision.base_url if vision else 'N/A'}, Model: {vision.model if vision else 'N/A'}"
    }
    
    if not success:
        logger.error("Vision服务连接失败，无法继续测试")
        # 生成报告
        report = generate_report(results, image_path)
        print("\n" + report)
        return 1
    
    # 测试2: 图像分析
    success, result = test_vision_image_analysis(vision, image_path)
    results['图像分析'] = {
        'success': success,
        'details': f"分析结果长度: {len(result) if result else 0} 字符",
        'result': result if result else None
    }
    
    # 测试3: 自定义提示词
    if success:
        success = test_vision_with_custom_prompts(vision, image_path)
        results['自定义提示词测试'] = {
            'success': success,
            'details': "测试了 3 个不同的提示词"
        }
    
    # 生成报告
    report = generate_report(results, image_path)
    print("\n" + report)
    
    # 保存报告
    report_file = os.path.join(
        os.path.dirname(__file__),
        f"vision_test_report_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n测试报告已保存到: {report_file}")
    
    # 返回退出码
    all_passed = all(r.get('success', False) for r in results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
