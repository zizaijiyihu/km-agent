"""
HR API用户信息服务
"""

import logging
import requests
from typing import Dict, Any, Optional

from .base import get_instance_key, get_cached_instance, set_cached_instance
from .exceptions import KsServiceError

logger = logging.getLogger(__name__)


class KsUserInfoService:
    """
    HR API用户信息服务封装类

    提供获取用户信息的功能，隐藏底层HTTP请求细节
    """

    def __init__(self, base_url: str, api_token: str):
        """
        初始化用户信息服务

        Args:
            base_url: HR API服务基础URL
            api_token: API访问令牌
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": api_token
        }

    def get_employee_info(self, email_prefix: str) -> Dict[str, Any]:
        """
        根据邮箱前缀获取员工信息

        Args:
            email_prefix: 员工邮箱前缀（如 lihaoze2）

        Returns:
            dict: 包含员工信息的字典，格式如下：
                {
                    "success": bool,
                    "data": {
                        "userId": str,
                        "userName": str,
                        "userNo": str,
                        "deptName": str,
                        "deptFullName": str,
                        "positionName": str,
                        "rank": str,
                        "location": str,
                        "sex": str,
                        "age": str,
                        "birthday": str,
                        "education": str,
                        "graduationInstitution": str,
                        "speciality": str,
                        "joinedDate": str,
                        "workAge": str,
                        "contractExpire": str,
                        ...
                    }
                }

        Raises:
            KsServiceError: 当请求失败或返回错误时抛出
        """
        url = f"{self.base_url}/{email_prefix}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result
                else:
                    raise KsServiceError(
                        f"HR API返回失败: {result}"
                    )
            else:
                raise KsServiceError(
                    f"HR API请求失败: {response.status_code} - {response.text}"
                )
        except requests.RequestException as e:
            raise KsServiceError(f"HR API请求异常: {e}")

    def get_employee_data(self, email_prefix: str) -> Optional[Dict[str, Any]]:
        """
        获取员工信息数据部分（便捷方法）

        Args:
            email_prefix: 员工邮箱前缀

        Returns:
            dict: 员工信息数据，如果失败返回None
        """
        try:
            result = self.get_employee_info(email_prefix)
            return result.get('data')
        except KsServiceError:
            return None


def ks_user_info(**kwargs) -> KsUserInfoService:
    """
    用户信息服务工厂函数

    Args:
        **kwargs: 传递给用户信息服务的参数

    Returns:
        KsUserInfoService: 用户信息服务对象
    """
    from ..configs.default import HR_API_CONFIG

    # 合并默认配置和传入参数
    config = {**HR_API_CONFIG, **kwargs}

    instance_key = get_instance_key("user_info", config)

    cached = get_cached_instance(instance_key)
    if cached is not None:
        return cached

    instance = KsUserInfoService(
        base_url=config['base_url'],
        api_token=config['api_token']
    )
    set_cached_instance(instance_key, instance)
    logger.info(f"User info service initialized with URL: {config['base_url']}")
    return instance
