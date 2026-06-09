"""
异环 NTE 养成计算器 - 数据库操作
使用 SQLite 存储用户录入的角色进度
"""
import sqlite3
import os
import json


class Database:
    """SQLite 数据库操作类"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_data.db')
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """确保数据库和表存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建角色进度表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    char_name TEXT NOT NULL,
                    curr_level INTEGER NOT NULL DEFAULT 1,
                    target_level INTEGER NOT NULL DEFAULT 80,
                    arc_name TEXT,
                    arc_curr_level INTEGER NOT NULL DEFAULT 0,
                    arc_target_level INTEGER NOT NULL DEFAULT 80,
                    remark TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

    def save_character_progress(self, char_name, curr_level, target_level,
                                arc_name=None, arc_curr_level=0, arc_target_level=80, remark=""):
        """保存角色进度"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 检查是否已存在
            cursor.execute('''
                SELECT id FROM character_progress WHERE char_name = ?
            ''', (char_name,))
            result = cursor.fetchone()

            if result:
                # 更新
                cursor.execute('''
                    UPDATE character_progress
                    SET curr_level = ?, target_level = ?, arc_name = ?,
                        arc_curr_level = ?, arc_target_level = ?, remark = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE char_name = ?
                ''', (curr_level, target_level, arc_name, arc_curr_level,
                      arc_target_level, remark, char_name))
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO character_progress
                    (char_name, curr_level, target_level, arc_name,
                     arc_curr_level, arc_target_level, remark)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (char_name, curr_level, target_level, arc_name,
                      arc_curr_level, arc_target_level, remark))

            conn.commit()

    def get_character_progress(self, char_name=None):
        """获取角色进度"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if char_name:
                cursor.execute('''
                    SELECT * FROM character_progress WHERE char_name = ?
                ''', (char_name,))
                result = cursor.fetchone()
                if result:
                    return self._row_to_dict(result)
                return None

            cursor.execute('''
                SELECT * FROM character_progress ORDER BY updated_at DESC
            ''')
            results = cursor.fetchall()
            return [self._row_to_dict(row) for row in results]

    def delete_character_progress(self, char_name):
        """删除角色进度"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM character_progress WHERE char_name = ?
            ''', (char_name,))
            conn.commit()

    def save_setting(self, key, value):
        """保存用户配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO user_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, json.dumps(value)))

            conn.commit()

    def get_setting(self, key, default=None):
        """获取用户配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT value FROM user_settings WHERE key = ?
            ''', (key,))
            result = cursor.fetchone()

            if result:
                return json.loads(result[0])
            return default

    def _row_to_dict(self, row):
        """将数据库行转换为字典"""
        return {
            'id': row[0],
            'char_name': row[1],
            'curr_level': row[2],
            'target_level': row[3],
            'arc_name': row[4],
            'arc_curr_level': row[5],
            'arc_target_level': row[6],
            'remark': row[7],
            'created_at': row[8],
            'updated_at': row[9]
        }
