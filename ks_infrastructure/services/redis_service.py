"""
Redis服务
"""

import logging
import redis
from .base import get_instance_key, get_cached_instance, set_cached_instance
from .exceptions import KsConnectionError

logger = logging.getLogger(__name__)


def ks_redis(**kwargs) -> redis.Redis:
    """
    Redis服务工厂函数

    Args:
        **kwargs: 传递给redis.Redis的参数

    Returns:
        redis.Redis: Redis客户端对象

    Raises:
        KsConnectionError: 当连接失败时抛出
    """
    from ..configs import REDIS_CONFIG

    # 合并默认配置和传入参数
    config = {
        'host': REDIS_CONFIG['host'],
        'port': REDIS_CONFIG['port'],
        'password': REDIS_CONFIG['password'],
        'db': REDIS_CONFIG.get('db', 0),
        'decode_responses': True  # 默认解码响应为字符串
    }
    config.update(kwargs)

    instance_key = get_instance_key("redis", config)

    cached = get_cached_instance(instance_key)
    if cached is not None:
        return cached

    try:
        instance = redis.Redis(**config)
        # 尝试ping一下以验证连接
        instance.ping()
        set_cached_instance(instance_key, instance)
        logger.info(f"Redis client connected to {config.get('host')}:{config.get('port')}")
        return instance
    except Exception as e:
        raise KsConnectionError(f"Redis连接失败: {e}")
