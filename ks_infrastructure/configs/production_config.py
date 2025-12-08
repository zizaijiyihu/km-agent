"""
生产环境配置文件 (Production Config)

此文件用于覆盖默认配置 (default.py)。
如果此文件存在，系统将优先使用此文件中的配置。
请勿将包含敏感信息的此文件提交到版本控制系统。
"""

# MySQL数据库配置
MYSQL_CONFIG = {
    "host": "120.92.109.164",
    "port": 8306,
    "user": "admin",
    "password": "rsdyxjh",
    "database": "yanzhi"
}

# MinIO对象存储配置
MINIO_CONFIG = {
    "endpoint": "http://120.92.109.164:9000",  # S3 API服务端口
    "access_key": "admin",
    "secret_key": "rsdyxjh110!",
    "region": "us-east-1"
}

# Qdrant向量数据库配置
QDRANT_CONFIG = {
    "url": "http://120.92.109.164:6333",
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
    "api_key": "sk-412a5b410f664d60a29327fdfa28ac6e",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-vl-max"
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
    "host": "120.92.109.164",
    "port": 6379,
    "password": "o5kT7Qy%Wb@3nL9pXz!a2DqR",
    "db": 0
}