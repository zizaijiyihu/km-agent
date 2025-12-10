#!/usr/bin/env python3
"""
Qdrant 服务测试脚本

测试内容：
1. Qdrant 服务连接
2. 创建新 collection
3. 插入向量数据
4. 搜索向量数据
5. 删除 collection (清理)
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from qdrant_client.models import Distance, VectorParams, PointStruct
from ks_infrastructure.services.qdrant_service import ks_qdrant
from ks_infrastructure.services.exceptions import KsConnectionError


def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")


def test_qdrant_connection():
    """测试 1: Qdrant 服务连接"""
    print_section("测试 1: Qdrant 服务连接")
    
    # 先测试网络连通性
    from ks_infrastructure.configs import QDRANT_CONFIG
    print(f"Qdrant 服务地址: {QDRANT_CONFIG.get('url')}")
    
    # 测试网络连接
    import socket
    import urllib.parse
    
    parsed_url = urllib.parse.urlparse(QDRANT_CONFIG.get('url'))
    host = parsed_url.hostname
    port = parsed_url.port or 6333
    
    print(f"\n正在测试网络连接 {host}:{port} ...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"✅ TCP 连接成功 ({host}:{port})")
        else:
            print(f"❌ TCP 连接失败 ({host}:{port}), 错误码: {result}")
            print("\n可能的原因:")
            print("  1. Qdrant 服务未启动")
            print("  2. 防火墙阻止连接")
            print("  3. 网络路由问题")
            return None
    except socket.timeout:
        print(f"❌ 连接超时 ({host}:{port})")
        return None
    except Exception as e:
        print(f"❌ 网络测试失败: {e}")
        return None
    
    # 尝试连接 Qdrant 服务
    print("\n正在创建 Qdrant 客户端...")
    try:
        # 添加超时参数
        client = ks_qdrant(timeout=60)
        print("✅ 成功创建 Qdrant 客户端")
        
        # 获取服务器信息
        print("正在获取 collections 列表...")
        collections = client.get_collections()
        print(f"✅ 当前 collections 数量: {len(collections.collections)}")
        
        if collections.collections:
            print("\n现有 Collections:")
            for col in collections.collections:
                print(f"  - {col.name}")
        
        return client
    except KsConnectionError as e:
        print(f"❌ Qdrant 连接失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
        return None


def test_create_collection(client, collection_name="test_qdrant_collection"):
    """测试 2: 创建新 collection"""
    print_section(f"测试 2: 创建新 Collection '{collection_name}'")
    
    try:
        # 检查 collection 是否已存在
        collections = client.get_collections()
        existing_names = [col.name for col in collections.collections]
        
        if collection_name in existing_names:
            print(f"⚠️  Collection '{collection_name}' 已存在，先删除...")
            client.delete_collection(collection_name)
            print(f"✅ 已删除旧的 collection")
        
        # 创建新 collection (向量维度: 128, 距离度量: Cosine)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=128,  # 向量维度
                distance=Distance.COSINE  # 余弦相似度
            )
        )
        print(f"✅ 成功创建 collection: {collection_name}")
        print(f"   - 向量维度: 128")
        print(f"   - 距离度量: COSINE")
        
        # 验证创建结果
        collection_info = client.get_collection(collection_name)
        print(f"\nCollection 详细信息:")
        print(f"  - 名称: {collection_info.config.params.vectors.size}")
        print(f"  - 向量数: {collection_info.points_count}")
        print(f"  - 状态: {collection_info.status}")
        
        return True
    except Exception as e:
        print(f"❌ 创建 collection 失败: {e}")
        return False


def test_insert_vectors(client, collection_name="test_qdrant_collection"):
    """测试 3: 插入向量数据"""
    print_section("测试 3: 插入向量数据")
    
    try:
        # 准备测试数据
        test_vectors = [
            {
                "id": 1,
                "vector": [0.1] * 128,  # 128 维向量
                "payload": {
                    "name": "测试文档 1",
                    "category": "技术文档",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "id": 2,
                "vector": [0.2] * 128,
                "payload": {
                    "name": "测试文档 2",
                    "category": "产品文档",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "id": 3,
                "vector": [0.3] * 128,
                "payload": {
                    "name": "测试文档 3",
                    "category": "用户手册",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        # 构建 points
        points = [
            PointStruct(
                id=vec["id"],
                vector=vec["vector"],
                payload=vec["payload"]
            )
            for vec in test_vectors
        ]
        
        # 插入数据
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"✅ 成功插入 {len(points)} 个向量")
        
        # 验证插入结果
        collection_info = client.get_collection(collection_name)
        print(f"✅ Collection 当前向量数: {collection_info.points_count}")
        
        return True
    except Exception as e:
        print(f"❌ 插入向量失败: {e}")
        return False


def test_search_vectors(client, collection_name="test_qdrant_collection"):
    """测试 4: 搜索向量数据"""
    print_section("测试 4: 搜索向量数据")
    
    try:
        # 准备查询向量 (接近第一个测试向量)
        query_vector = [0.15] * 128
        
        # 执行搜索
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=3
        )
        
        print(f"✅ 搜索完成，找到 {len(search_results)} 个结果\n")
        
        # 打印搜索结果
        for i, result in enumerate(search_results, 1):
            print(f"结果 #{i}:")
            print(f"  - ID: {result.id}")
            print(f"  - Score: {result.score:.4f}")
            print(f"  - 名称: {result.payload.get('name')}")
            print(f"  - 分类: {result.payload.get('category')}")
            print()
        
        return True
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return False


def test_cleanup(client, collection_name="test_qdrant_collection"):
    """测试 5: 清理测试数据"""
    print_section("测试 5: 清理测试数据")
    
    try:
        # 删除测试 collection
        client.delete_collection(collection_name)
        print(f"✅ 已删除测试 collection: {collection_name}")
        
        # 验证删除结果
        collections = client.get_collections()
        existing_names = [col.name for col in collections.collections]
        
        if collection_name not in existing_names:
            print(f"✅ 确认 collection 已被删除")
        else:
            print(f"⚠️  Collection 仍然存在")
        
        return True
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Qdrant 服务测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    test_collection_name = "test_qdrant_collection"
    results = []
    
    # 测试 1: 连接
    client = test_qdrant_connection()
    if client is None:
        print("\n❌ 无法连接到 Qdrant 服务，测试中止")
        return
    results.append(("连接测试", True))
    
    # 测试 2: 创建 collection
    success = test_create_collection(client, test_collection_name)
    results.append(("创建 Collection", success))
    if not success:
        return
    
    # 测试 3: 插入向量
    success = test_insert_vectors(client, test_collection_name)
    results.append(("插入向量", success))
    
    # 测试 4: 搜索向量
    success = test_search_vectors(client, test_collection_name)
    results.append(("搜索向量", success))
    
    # 测试 5: 清理
    success = test_cleanup(client, test_collection_name)
    results.append(("清理数据", success))
    
    # 打印测试总结
    print_section("测试总结")
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20s} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 个测试失败")


if __name__ == "__main__":
    run_all_tests()
