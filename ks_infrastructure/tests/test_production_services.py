#!/usr/bin/env python3
"""
生产环境服务测试脚本
测试 MinIO, Qdrant, MySQL, Redis 服务的连接性和基本功能
"""

import sys
import os
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Tuple

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ks_infrastructure.services.minio_service import ks_minio
from ks_infrastructure.services.mysql_service import ks_mysql
from ks_infrastructure.services.qdrant_service import ks_qdrant
from ks_infrastructure.services.redis_service import ks_redis

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """测试结果类"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.connection_success = False
        self.operations_success = False
        self.error_message = ""
        self.details = []
    
    def add_detail(self, detail: str):
        """添加测试详情"""
        self.details.append(detail)
    
    def set_error(self, error: str):
        """设置错误信息"""
        self.error_message = error
    
    def is_success(self) -> bool:
        """判断测试是否成功"""
        return self.connection_success and self.operations_success


def test_minio() -> TestResult:
    """测试MinIO连接和基本操作"""
    result = TestResult("MinIO")
    bucket_name = "test-bucket-temp"
    test_file_key = f"test-file-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    test_content = b"Test content for MinIO"
    
    try:
        # 连接测试
        result.add_detail("正在连接 MinIO...")
        client = ks_minio()
        result.connection_success = True
        result.add_detail("✓ MinIO 连接成功")
        
        # 列出所有存储桶
        result.add_detail("正在列出存储桶...")
        buckets = client.list_buckets()
        result.add_detail(f"✓ 找到 {len(buckets['Buckets'])} 个存储桶")
        
        # 创建测试桶（如果不存在）
        result.add_detail(f"正在检查测试桶 '{bucket_name}'...")
        try:
            client.head_bucket(Bucket=bucket_name)
            result.add_detail(f"✓ 测试桶 '{bucket_name}' 已存在")
        except client.exceptions.NoSuchBucket:
            result.add_detail(f"测试桶 '{bucket_name}' 不存在，正在创建...")
            client.create_bucket(Bucket=bucket_name)
            result.add_detail(f"✓ 测试桶 '{bucket_name}' 创建成功")
        except Exception as e:
            # 可能没有权限或其他问题，使用已存在的桶
            result.add_detail(f"! 无法检查/创建测试桶: {e}")
            # 尝试使用第一个可用的桶
            if buckets['Buckets']:
                bucket_name = buckets['Buckets'][0]['Name']
                result.add_detail(f"使用已存在的桶: {bucket_name}")
        
        # 上传测试文件
        result.add_detail(f"正在上传测试文件 '{test_file_key}'...")
        client.put_object(
            Bucket=bucket_name,
            Key=test_file_key,
            Body=test_content
        )
        result.add_detail(f"✓ 文件上传成功")
        
        # 下载测试文件
        result.add_detail(f"正在下载测试文件...")
        response = client.get_object(Bucket=bucket_name, Key=test_file_key)
        downloaded_content = response['Body'].read()
        
        if downloaded_content == test_content:
            result.add_detail(f"✓ 文件下载成功，内容验证通过")
        else:
            result.add_detail(f"✗ 文件内容不匹配")
            result.set_error("文件内容验证失败")
        
        # 删除测试文件
        result.add_detail(f"正在删除测试文件...")
        client.delete_object(Bucket=bucket_name, Key=test_file_key)
        result.add_detail(f"✓ 测试文件已清理")
        
        result.operations_success = True
        
    except Exception as e:
        error_msg = f"MinIO测试失败: {str(e)}\n{traceback.format_exc()}"
        result.set_error(error_msg)
        logger.error(error_msg)
    
    return result


def test_qdrant() -> TestResult:
    """测试Qdrant连接和基本操作"""
    result = TestResult("Qdrant")
    collection_name = f"test_collection_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        # 连接测试
        result.add_detail("正在连接 Qdrant...")
        client = ks_qdrant()
        result.connection_success = True
        result.add_detail("✓ Qdrant 连接成功")
        
        # 获取集合列表
        result.add_detail("正在获取集合列表...")
        collections = client.get_collections()
        result.add_detail(f"✓ 找到 {len(collections.collections)} 个集合")
        
        # 创建测试集合
        result.add_detail(f"正在创建测试集合 '{collection_name}'...")
        from qdrant_client.models import Distance, VectorParams
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE)
        )
        result.add_detail(f"✓ 测试集合创建成功")
        
        # 插入测试向量
        result.add_detail("正在插入测试向量...")
        from qdrant_client.models import PointStruct
        
        points = [
            PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"test": "data1"}),
            PointStruct(id=2, vector=[0.5, 0.6, 0.7, 0.8], payload={"test": "data2"})
        ]
        client.upsert(collection_name=collection_name, points=points)
        result.add_detail(f"✓ 向量插入成功")
        
        # 搜索测试
        result.add_detail("正在执行向量搜索...")
        search_result = client.search(
            collection_name=collection_name,
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=2
        )
        result.add_detail(f"✓ 搜索成功，找到 {len(search_result)} 个结果")
        
        # 删除测试集合
        result.add_detail(f"正在删除测试集合...")
        client.delete_collection(collection_name=collection_name)
        result.add_detail(f"✓ 测试集合已清理")
        
        result.operations_success = True
        
    except Exception as e:
        error_msg = f"Qdrant测试失败: {str(e)}\n{traceback.format_exc()}"
        result.set_error(error_msg)
        logger.error(error_msg)
    
    return result


def test_mysql() -> TestResult:
    """测试MySQL连接和基本操作"""
    result = TestResult("MySQL")
    test_table = f"test_table_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    conn = None
    cursor = None
    
    try:
        # 连接测试
        result.add_detail("正在连接 MySQL...")
        conn = ks_mysql()
        result.connection_success = True
        result.add_detail("✓ MySQL 连接成功")
        
        cursor = conn.cursor()
        
        # 获取数据库版本
        result.add_detail("正在获取数据库版本...")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        result.add_detail(f"✓ MySQL 版本: {version}")
        
        # 创建测试表
        result.add_detail(f"正在创建测试表 '{test_table}'...")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {test_table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        result.add_detail(f"✓ 测试表创建成功")
        
        # 插入测试数据
        result.add_detail("正在插入测试数据...")
        cursor.execute(f"INSERT INTO {test_table} (name) VALUES (%s)", ("test_data",))
        conn.commit()
        result.add_detail(f"✓ 数据插入成功")
        
        # 查询测试数据
        result.add_detail("正在查询测试数据...")
        cursor.execute(f"SELECT * FROM {test_table}")
        rows = cursor.fetchall()
        result.add_detail(f"✓ 查询成功，找到 {len(rows)} 条记录")
        
        # 删除测试表
        result.add_detail(f"正在删除测试表...")
        cursor.execute(f"DROP TABLE IF EXISTS {test_table}")
        conn.commit()
        result.add_detail(f"✓ 测试表已清理")
        
        result.operations_success = True
        
    except Exception as e:
        error_msg = f"MySQL测试失败: {str(e)}\n{traceback.format_exc()}"
        result.set_error(error_msg)
        logger.error(error_msg)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return result


def test_redis() -> TestResult:
    """测试Redis连接和基本操作"""
    result = TestResult("Redis")
    test_key = f"test_key_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    test_value = "test_value"
    
    try:
        # 连接测试
        result.add_detail("正在连接 Redis...")
        client = ks_redis()
        result.connection_success = True
        result.add_detail("✓ Redis 连接成功")
        
        # Ping测试
        result.add_detail("正在执行 PING 命令...")
        pong = client.ping()
        result.add_detail(f"✓ PING 响应: {pong}")
        
        # 获取Redis信息
        result.add_detail("正在获取 Redis 信息...")
        info = client.info()
        result.add_detail(f"✓ Redis 版本: {info.get('redis_version', 'unknown')}")
        result.add_detail(f"✓ 数据库大小: {client.dbsize()} 个键")
        
        # SET测试
        result.add_detail(f"正在设置键值对 '{test_key}'...")
        client.set(test_key, test_value, ex=60)  # 60秒过期
        result.add_detail(f"✓ 键值设置成功")
        
        # GET测试
        result.add_detail(f"正在获取键值...")
        retrieved_value = client.get(test_key)
        if retrieved_value == test_value:
            result.add_detail(f"✓ 键值获取成功，内容验证通过")
        else:
            result.add_detail(f"✗ 键值不匹配: 期望 '{test_value}'，实际 '{retrieved_value}'")
            result.set_error("键值验证失败")
        
        # DELETE测试
        result.add_detail(f"正在删除测试键...")
        client.delete(test_key)
        result.add_detail(f"✓ 测试键已清理")
        
        result.operations_success = True
        
    except Exception as e:
        error_msg = f"Redis测试失败: {str(e)}\n{traceback.format_exc()}"
        result.set_error(error_msg)
        logger.error(error_msg)
    
    return result


def generate_report(results: List[TestResult]) -> str:
    """生成测试报告"""
    report = []
    report.append("=" * 80)
    report.append("生产环境服务测试报告")
    report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    # 统计
    total = len(results)
    passed = sum(1 for r in results if r.is_success())
    failed = total - passed
    
    report.append(f"总计: {total} 个服务")
    report.append(f"通过: {passed} 个")
    report.append(f"失败: {failed} 个")
    report.append("")
    
    # 详细结果
    for result in results:
        report.append("-" * 80)
        report.append(f"服务: {result.service_name}")
        report.append(f"连接状态: {'✓ 成功' if result.connection_success else '✗ 失败'}")
        report.append(f"操作状态: {'✓ 成功' if result.operations_success else '✗ 失败'}")
        
        if result.error_message:
            report.append(f"错误信息: {result.error_message}")
        
        if result.details:
            report.append("\n详细信息:")
            for detail in result.details:
                report.append(f"  {detail}")
        
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """主函数"""
    print("开始测试生产环境服务...")
    print("")
    
    results = []
    
    # 测试所有服务
    services = [
        ("MinIO", test_minio),
        ("Qdrant", test_qdrant),
        ("MySQL", test_mysql),
        ("Redis", test_redis)
    ]
    
    for service_name, test_func in services:
        print(f"{'=' * 40}")
        print(f"测试 {service_name}...")
        print(f"{'=' * 40}")
        result = test_func()
        results.append(result)
        print("")
    
    # 生成报告
    report = generate_report(results)
    print(report)
    
    # 保存报告到文件
    report_file = os.path.join(
        os.path.dirname(__file__),
        f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n测试报告已保存到: {report_file}")
    
    # 返回退出码
    all_passed = all(r.is_success() for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
