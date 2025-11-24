"""
图片存储和解析服务

将图片存储到临时桶并使用视觉识别服务解析图片内容
"""

import logging
import base64
import os
import time
from typing import Dict, Any, Optional
from io import BytesIO

from file_repository import upload_file
from ks_infrastructure import ks_vision
from ks_infrastructure.configs.default import MINIO_CONFIG

logger = logging.getLogger(__name__)

# 默认提示词
DEFAULT_PROMPT = "提炼图片信息内容，重点关注非设计和排版的文字信息，直接提炼结构化信息。"


def analyze_temp_image(
    image_path: str,
    username: str = "system",
    prompt: str = DEFAULT_PROMPT,
    custom_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    存储图片到临时桶并解析图片内容

    Args:
        image_path: 本地图片文件路径
        username: 用户名，默认为 'system'
        prompt: 图片分析提示词，默认为通用描述提示
        custom_filename: 自定义文件名，如果不提供则使用原文件名

    Returns:
        dict: 包含以下字段：
            - success: bool, 是否成功
            - image_url: str, 图片的网络访问地址
            - analysis: str, 图片解析结果（带前缀）
            - error: str, 错误信息（仅当 success=False 时）

    Raises:
        FileNotFoundError: 当图片文件不存在时
        Exception: 其他处理异常
    """
    try:
        # 1. 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 2. 获取文件名和扩展名
        original_filename = os.path.basename(image_path)
        filename = custom_filename or original_filename
        basename, ext = os.path.splitext(filename)
        image_format = ext.lstrip('.').lower() or 'png'

        # 为 tmp 桶的文件添加时间戳后缀，避免文件名冲突
        timestamp = time.time()
        timestamp_int = int(timestamp)
        microsecond = int((timestamp - timestamp_int) * 1000000)
        filename_with_timestamp = f"{basename}_{timestamp_int}_{microsecond}{ext}"

        # 3. 读取图片文件
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 4. 上传到 tmp 桶
        logger.info(f"上传图片到 tmp 桶: {filename_with_timestamp}")
        file_stream = BytesIO(image_data)

        # 根据扩展名设置 content_type
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp'
        }
        content_type = content_type_map.get(image_format, 'image/png')

        object_key = upload_file(
            username=username,
            filename=filename_with_timestamp,
            file_data=file_stream,
            bucket='tmp',
            content_type=content_type,
            is_public=1  # 设置为公开，便于访问
        )
        logger.info(f"图片上传成功: {object_key}")

        # 5. 生成图片访问 URL
        # MinIO URL 格式: http://endpoint/bucket/object_key
        minio_endpoint = MINIO_CONFIG['endpoint'].rstrip('/')
        image_url = f"{minio_endpoint}/tmp/{object_key}"

        # 6. 转换为 base64 用于视觉分析
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 7. 调用视觉识别服务解析图片
        logger.info("调用视觉识别服务解析图片")
        vision_service = ks_vision()
        analysis_result = vision_service.analyze_image(
            image_base64=image_base64,
            image_format=image_format,
            prompt=prompt
        )

        # 8. 添加前缀
        formatted_analysis = f"【以下内容为图片理解结果】\n{analysis_result}"

        return {
            'success': True,
            'image_url': image_url,
            'analysis': formatted_analysis
        }

    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"图片分析失败: {e}")
        return {
            'success': False,
            'error': f"图片分析失败: {e}"
        }


def batch_analyze_images(
    image_paths: list[str],
    username: str = "system",
    prompt: str = DEFAULT_PROMPT
) -> list[Dict[str, Any]]:
    """
    批量分析多张图片

    Args:
        image_paths: 图片文件路径列表
        username: 用户名，默认为 'system'
        prompt: 图片分析提示词

    Returns:
        list[dict]: 分析结果列表，每个元素格式同 analyze_temp_image 返回值
    """
    results = []
    for image_path in image_paths:
        result = analyze_temp_image(
            image_path=image_path,
            username=username,
            prompt=prompt
        )
        results.append(result)
    return results
