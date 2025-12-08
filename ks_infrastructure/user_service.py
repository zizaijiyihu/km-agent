"""
User Service - 用户管理服务

提供统一的获取当前用户的方法，替代硬编码的默认用户。
"""
from flask import request, has_request_context
from ks_infrastructure.configs.default import DEFAULT_USER

def get_current_user() -> str:
    """
    获取当前用户
    
    如果是线上环境（通过Proxy），从Header里的X-User-Id获取。
    如果是测试环境（无Header），使用默认配置的用户名。
    
    Returns:
        str: 当前用户名
    """
    # 尝试从Flask请求上下文中获取
    if has_request_context():
        # 优先获取Header中的X-User-Id (线上环境)
        user_id = request.headers.get("X-User-Id")
        if user_id:
            return user_id
            
    # 如果不在请求上下文中，或者没有X-User-Id头（测试环境），返回默认用户
    return DEFAULT_USER
