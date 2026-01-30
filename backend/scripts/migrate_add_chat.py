"""
数据库迁移脚本 - 添加聊天消息表
用于升级现有数据库到支持多轮对话的版本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from core.dependencies import engine, logger


def migrate_add_chat_messages():
    """添加聊天消息表"""
    try:
        with engine.connect() as conn:
            # 检查表是否已存在
            result = conn.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='chat_messages'
            """)).fetchone()

            if result:
                logger.info("chat_messages 表已存在，跳过创建")
                return

            # 创建聊天消息表
            conn.execute(text("""
                CREATE TABLE chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    message_type VARCHAR(50),
                    extra_data JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES game_projects (id) ON DELETE CASCADE
                )
            """))

            # 创建索引
            conn.execute(text("""
                CREATE INDEX idx_chat_messages_project_id ON chat_messages(project_id)
            """))

            conn.commit()
            logger.info("✅ 成功创建 chat_messages 表")

    except Exception as e:
        logger.error(f"❌ 创建 chat_messages 表失败: {e}")
        raise


def migrate_update_gameproject_updated_at():
    """更新 game_projects 表，添加 onupdate 触发器"""
    try:
        with engine.connect() as conn:
            # 检查是否有 updated_at 列
            result = conn.execute(text("""
                PRAGMA table_info(game_projects)
            """)).fetchall()

            column_names = [row[1] for row in result]

            if 'updated_at' not in column_names:
                # 添加 updated_at 列
                conn.execute(text("""
                    ALTER TABLE game_projects
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                """))
                logger.info("✅ 成功添加 updated_at 列")

            # SQLite 不支持直接在表定义中添加 onupdate
            # 需要使用触发器
            conn.execute(text("""
                DROP TRIGGER IF EXISTS update_game_projects_timestamp
            """))

            conn.execute(text("""
                CREATE TRIGGER update_game_projects_timestamp
                AFTER UPDATE ON game_projects
                FOR EACH ROW
                BEGIN
                    UPDATE game_projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """))

            conn.commit()
            logger.info("✅ 成功添加 updated_at 触发器")

    except Exception as e:
        logger.error(f"❌ 添加 updated_at 触发器失败: {e}")
        raise


def run_migrations():
    """运行所有迁移"""
    logger.info("🚀 开始数据库迁移...")

    migrate_add_chat_messages()
    migrate_update_gameproject_updated_at()

    logger.info("✅ 数据库迁移完成！")


if __name__ == "__main__":
    run_migrations()
