"""
配置模块

导出配置，优先加载 production_config.py (如果存在)，否则使用 default.py。
"""

import logging

# 配置日志
logger = logging.getLogger(__name__)

# 1. 加载默认配置
from .default import (
    MYSQL_CONFIG,
    MINIO_CONFIG,
    QDRANT_CONFIG,
    OPENAI_CONFIG,
    EMBEDDING_CONFIG,
    VISION_CONFIG,
    HR_API_CONFIG,
    ADMIN_BACKDOOR_TOKEN,
    DEFAULT_USER,
    REDIS_CONFIG
)

# 2. 尝试加载生产环境配置并覆盖
try:
    from . import production_config
    
    # 覆盖配置
    if hasattr(production_config, 'MYSQL_CONFIG'):
        MYSQL_CONFIG = production_config.MYSQL_CONFIG
    if hasattr(production_config, 'MINIO_CONFIG'):
        MINIO_CONFIG = production_config.MINIO_CONFIG
    if hasattr(production_config, 'QDRANT_CONFIG'):
        QDRANT_CONFIG = production_config.QDRANT_CONFIG
    if hasattr(production_config, 'OPENAI_CONFIG'):
        OPENAI_CONFIG = production_config.OPENAI_CONFIG
    if hasattr(production_config, 'EMBEDDING_CONFIG'):
        EMBEDDING_CONFIG = production_config.EMBEDDING_CONFIG
    if hasattr(production_config, 'VISION_CONFIG'):
        VISION_CONFIG = production_config.VISION_CONFIG
    if hasattr(production_config, 'HR_API_CONFIG'):
        HR_API_CONFIG = production_config.HR_API_CONFIG
    if hasattr(production_config, 'ADMIN_BACKDOOR_TOKEN'):
        ADMIN_BACKDOOR_TOKEN = production_config.ADMIN_BACKDOOR_TOKEN
    if hasattr(production_config, 'DEFAULT_USER'):
        DEFAULT_USER = production_config.DEFAULT_USER
    if hasattr(production_config, 'REDIS_CONFIG'):
        REDIS_CONFIG = production_config.REDIS_CONFIG
        
    logger.info("已加载生产环境配置文件: production_config.py")

except ImportError:
    logger.info("未找到生产环境配置文件 production_config.py，使用默认配置。")

__all__ = [
    'MYSQL_CONFIG',
    'MINIO_CONFIG',
    'QDRANT_CONFIG',
    'OPENAI_CONFIG',
    'EMBEDDING_CONFIG',
    'VISION_CONFIG',
    'HR_API_CONFIG',
    'ADMIN_BACKDOOR_TOKEN',
    'DEFAULT_USER',
    'REDIS_CONFIG'
]
