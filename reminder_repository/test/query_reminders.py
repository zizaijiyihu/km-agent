#!/usr/bin/env python3
"""
提醒数据查询脚本（独立版本）

直接连接数据库查询提醒数据，不依赖项目模块
"""

import mysql.connector
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    "host": "120.92.109.164",
    "port": 8306,
    "user": "admin",
    "password": "rsdyxjh",
    "database": "yanzhi"
}

TABLE_NAME = "agent_reminders"


def get_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def query_all_reminders():
    """查询所有提醒"""
    print("=" * 100)
    print("📋 所有提醒列表")
    print("=" * 100)
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        sql = f"""
        SELECT id, content, is_public, user_id, created_at, updated_at
        FROM {TABLE_NAME}
        ORDER BY created_at DESC
        """
        
        cursor.execute(sql)
        reminders = cursor.fetchall()
        
        if not reminders:
            print("\n暂无提醒数据\n")
            return
        
        print(f"\n共 {len(reminders)} 条提醒\n")
        
        # 打印表头
        print(f"{'ID':<6} {'内容':<40} {'状态':<10} {'用户ID':<15} {'创建时间':<20}")
        print("-" * 100)
        
        # 打印数据
        for r in reminders:
            visibility = "🌐 公开" if r.get('is_public') == 1 else "🔒 私有"
            content = r.get('content', '')[:38] + '..' if len(r.get('content', '')) > 40 else r.get('content', '')
            user_id = r.get('user_id') or '-'
            created_at = r.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if r.get('created_at') else '-'
            
            print(f"{r.get('id'):<6} {content:<40} {visibility:<10} {user_id:<15} {created_at:<20}")
        
        # 统计信息
        public_count = sum(1 for r in reminders if r.get('is_public') == 1)
        private_count = sum(1 for r in reminders if r.get('is_public') == 0)
        
        print("\n" + "=" * 100)
        print(f"📊 统计:")
        print(f"  - 公开提醒: {public_count} 条")
        print(f"  - 私有提醒: {private_count} 条")
        
        # 按用户统计私有提醒
        if private_count > 0:
            user_stats = {}
            for r in reminders:
                if r.get('is_public') == 0:
                    user_id = r.get('user_id', 'unknown')
                    user_stats[user_id] = user_stats.get(user_id, 0) + 1
            
            print(f"\n👤 私有提醒按用户统计:")
            for user_id, count in user_stats.items():
                print(f"  - {user_id}: {count} 条")
        
        print()
        
    except mysql.connector.Error as e:
        print(f"\n❌ 查询失败: {e}\n")
    finally:
        cursor.close()
        conn.close()


def query_user_reminders(user_id):
    """查询指定用户的提醒（公开+私有）"""
    print("=" * 100)
    print(f"📋 用户 {user_id} 的提醒列表（公开 + 私有）")
    print("=" * 100)
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        sql = f"""
        SELECT id, content, is_public, user_id, created_at, updated_at
        FROM {TABLE_NAME}
        WHERE is_public = 1 OR (is_public = 0 AND user_id = %s)
        ORDER BY created_at DESC
        """
        
        cursor.execute(sql, (user_id,))
        reminders = cursor.fetchall()
        
        if not reminders:
            print(f"\n用户 {user_id} 暂无可见提醒\n")
            return
        
        print(f"\n共 {len(reminders)} 条可见提醒\n")
        
        # 打印表头
        print(f"{'ID':<6} {'内容':<40} {'状态':<10} {'用户ID':<15} {'创建时间':<20}")
        print("-" * 100)
        
        # 打印数据
        for r in reminders:
            visibility = "🌐 公开" if r.get('is_public') == 1 else "🔒 私有"
            content = r.get('content', '')[:38] + '..' if len(r.get('content', '')) > 40 else r.get('content', '')
            owner_id = r.get('user_id') or '-'
            created_at = r.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if r.get('created_at') else '-'
            
            print(f"{r.get('id'):<6} {content:<40} {visibility:<10} {owner_id:<15} {created_at:<20}")
        
        # 统计信息
        public_count = sum(1 for r in reminders if r.get('is_public') == 1)
        private_count = sum(1 for r in reminders if r.get('is_public') == 0 and r.get('user_id') == user_id)
        
        print("\n" + "=" * 100)
        print(f"📊 统计:")
        print(f"  - 公开提醒: {public_count} 条")
        print(f"  - 私有提醒: {private_count} 条")
        print()
        
    except mysql.connector.Error as e:
        print(f"\n❌ 查询失败: {e}\n")
    finally:
        cursor.close()
        conn.close()


def query_reminder_by_id(reminder_id):
    """查询单个提醒详情"""
    print("=" * 100)
    print(f"📋 提醒详情 (ID: {reminder_id})")
    print("=" * 100)
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        sql = f"""
        SELECT id, content, is_public, user_id, created_at, updated_at
        FROM {TABLE_NAME}
        WHERE id = %s
        """
        
        cursor.execute(sql, (reminder_id,))
        reminder = cursor.fetchone()
        
        if not reminder:
            print(f"\n❌ 提醒不存在 (ID: {reminder_id})\n")
            return
        
        visibility = "🌐 公开" if reminder.get('is_public') == 1 else "🔒 私有"
        created_at = reminder.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if reminder.get('created_at') else '-'
        updated_at = reminder.get('updated_at').strftime('%Y-%m-%d %H:%M:%S') if reminder.get('updated_at') else '-'
        
        print(f"\nID: {reminder.get('id')}")
        print(f"内容: {reminder.get('content')}")
        print(f"状态: {visibility}")
        print(f"用户ID: {reminder.get('user_id') or '-'}")
        print(f"创建时间: {created_at}")
        print(f"更新时间: {updated_at}")
        print()
        
    except mysql.connector.Error as e:
        print(f"\n❌ 查询失败: {e}\n")
    finally:
        cursor.close()
        conn.close()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) == 1:
        # 默认查询所有
        query_all_reminders()
    elif len(sys.argv) == 3:
        if sys.argv[1] in ['--user', '-u']:
            query_user_reminders(sys.argv[2])
        elif sys.argv[1] in ['--id', '-i']:
            try:
                reminder_id = int(sys.argv[2])
                query_reminder_by_id(reminder_id)
            except ValueError:
                print("❌ 错误: ID 必须是数字")
        else:
            print_usage()
    else:
        print_usage()


def print_usage():
    """打印使用说明"""
    print("""
使用方法:
  python3 query_reminders.py                    # 查询所有提醒
  python3 query_reminders.py --user huxiaoxiao  # 查询指定用户的提醒
  python3 query_reminders.py --id 1             # 查询指定ID的提醒详情
  
参数说明:
  --user, -u <用户ID>    查询指定用户的提醒（公开 + 私有）
  --id, -i <提醒ID>      查询指定ID的提醒详情
    """)


if __name__ == "__main__":
    main()
