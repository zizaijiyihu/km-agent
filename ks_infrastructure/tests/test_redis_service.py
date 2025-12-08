import unittest
import sys
import os

# Add the project root to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ks_infrastructure.services.redis_service import ks_redis

class TestRedisService(unittest.TestCase):
    def test_redis_connection_and_operations(self):
        print("\nTesting Redis Service...")
        try:
            # 获取Redis客户端
            r = ks_redis()
            
            # 测试设置值
            test_key = "test_key_ks_infrastructure"
            test_value = "hello_redis"
            print(f"Setting key '{test_key}' to '{test_value}'")
            r.set(test_key, test_value)
            
            # 测试获取值
            value = r.get(test_key)
            print(f"Got value: '{value}'")
            self.assertEqual(value, test_value)
            
            # 清理测试数据
            r.delete(test_key)
            print("Cleaned up test key.")
            
            print("Redis service test passed successfully.")
            
        except Exception as e:
            self.fail(f"Redis service test failed: {e}")

if __name__ == '__main__':
    unittest.main()
