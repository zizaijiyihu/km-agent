"""
生产环境配置文件 (Production Config)

此文件用于覆盖默认配置 (default.py)。
如果此文件存在，系统将优先使用此文件中的配置。
请勿将包含敏感信息的此文件提交到版本控制系统。
"""

# MySQL数据库配置
MYSQL_CONFIG = {
    "host": "10.69.68.226",
    "port": 8306,
    "user": "root",
    "password": "Kingsoft_com123!",
    "database": "yanzhi"
}

# MinIO对象存储配置
MINIO_CONFIG = {
    "endpoint": "http://10.69.68.226:8900",  # MinIO API endpoint
    "access_key": "admin",
    "secret_key": "rsdyxjh110!",
    "region": "us-east-1"
}

# Qdrant向量数据库配置
QDRANT_CONFIG = {
    "url": "http://10.69.68.226:8933",
    "api_key": "rsdyxjh"
}

# OpenAI大语言模型配置
OPENAI_CONFIG = {
    "api_key": "73e6f0a3-c154-4ad4-bb7b-912f2c498e3e",
    "base_url": "https://kspmas.ksyun.com/v1/",
    "model": "deepseek-v3.1"
}

# Embedding服务配置
EMBEDDING_CONFIG = {
    "url": "http://10.69.86.20/v1/embeddings",
    "api_key": "7c64b222-4988-4e6a-bb26-48594ceda8a9"
}

# Vision视觉识别服务配置
VISION_CONFIG = {
    "api_key": "73e6f0a3-c154-4ad4-bb7b-912f2c498e3e",
    "base_url": "https://kspmas.ksyun.com/v1/",
    "model": "qwen3-vl-235b-a22b-instruct"
}

# HR API用户信息服务配置
HR_API_CONFIG = {
    "base_url": "http://10.69.87.93:8001/api/hr/employee",
    "api_token": "demo-api-token-please-change-this"
}

# Admin后门认证Token（可按需修改）
ADMIN_BACKDOOR_TOKEN = "5HYRM0GR17DCVB@MMKI"

# 默认用户配置（用于测试环境）
DEFAULT_USER = "huxiaoxiao"

# Redis配置
REDIS_CONFIG = {
    "host": "10.69.68.226",
    "port": 8378,
    "password": "Zu5GpNWDO&wlHxgS",
    "db": 0
}