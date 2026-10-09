"""测试数据清理(直连 SQLite,仅用于测试环境)

- clean_flow_reservations: 只清链路用例日期的预订,链路用例自愈用,并发安全
- clean_test_data:         完整清理(链路预订 + 注册用户),仅串行模式会话级调用
"""
import os
import sqlite3

import config


def _execute(sql: str, params=()):
    if not os.path.exists(config.TEST_DB_PATH):
        return
    conn = sqlite3.connect(config.TEST_DB_PATH, timeout=10)
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def clean_flow_reservations():
    """删除链路用例日期上的预订(含级联历史)。

    链路用例开头调用:若上一次运行/重试中途失败,残留的 pending 预订
    无法通过 API 删除(接口只允许删 completed/cancelled),只能直连清理。
    """
    placeholders = ','.join('?' * len(config.FLOW_RESERVATION_DATES))
    _execute(
        f'DELETE FROM reservations WHERE reservation_date IN ({placeholders})',
        config.FLOW_RESERVATION_DATES)


def clean_test_data():
    """完整清理:链路用例的预订 + 注册用例的用户(级联删除其预订与历史)"""
    clean_flow_reservations()
    _execute("DELETE FROM users WHERE email LIKE 'auto_test_%'")
