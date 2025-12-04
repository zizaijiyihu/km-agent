#!/usr/bin/env python3
"""清空提醒数据库脚本（使用 mysql_service 连接池）

警告：此脚本会删除 agent_reminders 表中的所有数据！
"""

import os
import sys

# 将项目根目录加入模块搜索路径，便于直接运行此脚本
# __file__ 位于 reminder_repository/test/clear_reminders.py
# 需要向上三级到项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ks_infrastructure.db_session import db_session
from ks_infrastructure.services.exceptions import KsConnectionError

TABLE_NAME = "agent_reminders"


def count_reminders():
    """统计提醒数量"""
    try:
        with db_session(dictionary=True) as cursor:
            cursor.execute(f"SELECT COUNT(*) AS count FROM {TABLE_NAME}")
            row = cursor.fetchone()
            return row["count"] if row else 0
    except KsConnectionError as e:
        print(f"❌ 查询失败: {e}")
        return 0


def clear_reminders(confirm=True):
    """清空所有提醒"""
    # 先统计数量
    count = count_reminders()
    
    if count == 0:
        print("\n✅ 数据库中没有提醒数据，无需清空。\n")
        return
    
    print(f"\n⚠️  警告：即将删除 {count} 条提醒数据！")
    
    if confirm:
        print("\n请确认是否继续？")
        response = input("输入 'yes' 确认删除，其他任何输入取消: ")
        
        if response.lower() != 'yes':
            print("\n❌ 操作已取消。\n")
            return
    
    try:
        # 删除所有数据并重置自增ID
        with db_session(auto_commit=False) as cursor:
            cursor.execute(f"DELETE FROM {TABLE_NAME}")
            deleted_count = cursor.rowcount
            cursor.execute(f"ALTER TABLE {TABLE_NAME} AUTO_INCREMENT = 1")
            cursor.connection.commit()

        print(f"\n✅ 成功删除 {deleted_count} 条提醒数据。")
        print("✅ 已重置自增ID。\n")

    except KsConnectionError as e:
        print(f"\n❌ 删除失败: {e}\n")
    except Exception as e:
        # 保持提示友好，便于排查
        print(f"\n❌ 删除或重置失败: {e}\n")


def show_current_data():
    """显示当前数据"""
    try:
        with db_session(dictionary=True) as cursor:
            sql = f"""
            SELECT id, content, is_public, user_id, created_at
            FROM {TABLE_NAME}
            ORDER BY created_at DESC
            LIMIT 10
            """
            cursor.execute(sql)
            reminders = cursor.fetchall()

        if not reminders:
            print("\n数据库中没有提醒数据。\n")
            return
        
        print("\n" + "="*80)
        print("当前提醒数据（最多显示10条）")
        print("="*80)
        
        for r in reminders:
            visibility = "🌐 公开" if r.get('is_public') == 1 else "🔒 私有"
            content = r.get('content', '')[:40] + '...' if len(r.get('content', '')) > 40 else r.get('content', '')
            user_id = r.get('user_id') or '-'
            created_at = r.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if r.get('created_at') else '-'
            
            print(f"ID {r.get('id')}: {content}")
            print(f"  状态: {visibility} | 用户: {user_id} | 创建: {created_at}")
            print()
        
        total = count_reminders()
        if total > 10:
            print(f"... 还有 {total - 10} 条数据未显示")
        print(f"总计: {total} 条提醒\n")

    except KsConnectionError as e:
        print(f"\n❌ 查询失败: {e}\n")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='清空提醒数据库',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 clear_reminders.py              # 显示当前数据并确认后删除
  python3 clear_reminders.py --show       # 只显示当前数据
  python3 clear_reminders.py --force      # 不确认直接删除（危险！）
        """
    )
    
    parser.add_argument('--show', '-s', action='store_true', help='只显示当前数据，不删除')
    parser.add_argument('--force', '-f', action='store_true', help='不确认直接删除（危险！）')
    
    args = parser.parse_args()
    
    if args.show:
        # 只显示数据
        show_current_data()
    else:
        # 显示数据并删除
        show_current_data()
        clear_reminders(confirm=not args.force)


if __name__ == "__main__":
    main()
