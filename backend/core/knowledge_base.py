"""
RAG知识库模块 - 管理游戏模板和向量检索
使用ChromaDB进行向量存储和相似度搜索
"""
import os
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from core.dependencies import logger

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB未安装，使用内存知识库")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI未安装，使用简单知识库")


class GameTemplateDB:
    """游戏模板数据库 - 使用RAG检索相似游戏模板"""

    def __init__(self):
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.embeddings_cache: Dict[str, List[float]] = {}
        self.collection = None
        self.is_initialized = False

    async def initialize(self):
        """初始化知识库"""
        try:
            logger.info("初始化游戏模板知识库")

            if CHROMADB_AVAILABLE:
                # 使用ChromaDB
                client = chromadb.PersistentClient(path="./data/chroma_db")
                self.collection = client.get_or_create_collection(
                    name="game_templates",
                    metadata={"description": "游戏模板向量数据库"}
                )

                # 检查是否需要初始化数据
                if self.collection.count() == 0:
                    await self._preload_templates()

            # 总是加载模板到内存
            await self._load_templates()

            self.is_initialized = True
            logger.info("游戏模板知识库初始化完成")

        except Exception as e:
            logger.error(f"知识库初始化失败: {e}")
            self.is_initialized = False

    async def _load_templates(self):
        """加载游戏模板"""
        templates = [
            {
                "id": "snake_game",
                "name": "贪吃蛇",
                "description": "经典的贪吃蛇游戏，控制蛇吃食物变长",
                "game_type": "贪吃蛇",
                "tech_stack": "Vanilla JS + Canvas API",
                "mechanics": ["蛇的移动", "食物生成", "碰撞检测", "得分系统", "游戏结束"],
                "file_structure": {
                    "index.html": "主页面",
                    "styles.css": "样式文件",
                    "game.js": "游戏逻辑"
                },
                "reference_code": "snake_template",
                "keywords": ["蛇", "吃", "移动", "canvas", "2D", "经典", "简单", "休闲"]
            },
            {
                "id": "brick_breaker",
                "name": "打砖块",
                "description": "用挡板接球并打破所有砖块",
                "game_type": "打砖块",
                "tech_stack": "Vanilla JS + Canvas API",
                "mechanics": ["挡板控制", "球体物理", "砖块碰撞", "生命系统", "关卡设计"],
                "file_structure": {
                    "index.html": "主页面",
                    "styles.css": "样式文件",
                    "game.js": "游戏逻辑"
                },
                "reference_code": "brick_breaker_template",
                "keywords": ["挡板", "球", "砖块", "反弹", "经典", "街机", "消除"]
            },
            {
                "id": "whack_a_mole",
                "name": "打地鼠",
                "description": "点击随机出现的地鼠得分",
                "game_type": "打地鼠",
                "tech_stack": "Vanilla JS + DOM操作",
                "mechanics": ["随机出现", "点击判定", "时间限制", "计分系统", "难度递增"],
                "file_structure": {
                    "index.html": "主页面",
                    "styles.css": "样式文件",
                    "game.js": "游戏逻辑"
                },
                "reference_code": "whack_mole_template",
                "keywords": ["地鼠", "点击", "反应", "速度", "儿童", "休闲", "趣味"]
            },
            {
                "id": "dodge_ball",
                "name": "躲避球",
                "description": "躲避不断出现的障碍物",
                "game_type": "躲避球",
                "tech_stack": "Vanilla JS + Canvas API",
                "mechanics": ["玩家移动", "障碍物生成", "碰撞检测", "生存时间", "得分系统"],
                "file_structure": {
                    "index.html": "主页面",
                    "styles.css": "样式文件",
                    "game.js": "游戏逻辑"
                },
                "reference_code": "dodge_ball_template",
                "keywords": ["躲避", "障碍", "移动", "生存", "反应", "速度", "挑战"]
            },
            {
                "id": "guess_number",
                "name": "猜数字",
                "description": "猜测随机生成的数字",
                "game_type": "猜数字",
                "tech_stack": "Vanilla JS + DOM操作",
                "mechanics": ["随机数生成", "输入判断", "提示反馈", "尝试次数", "胜利条件"],
                "file_structure": {
                    "index.html": "主页面",
                    "styles.css": "样式文件",
                    "game.js": "游戏逻辑"
                },
                "reference_code": "guess_number_template",
                "keywords": ["数字", "猜测", "逻辑", "益智", "简单", "儿童", "教育"]
            },
            {
                "id": "tetris",
                "name": "俄罗斯方块",
                "description": "经典方块消除游戏",
                "game_type": "俄罗斯方块",
                "tech_stack": "Vanilla JS + Canvas API",
                "mechanics": ["方块下落", "移动旋转", "行消除", "得分系统", "等级系统"],
                "file_structure": {
                    "index.html": "主页面",
                    "styles.css": "样式文件",
                    "game.js": "游戏逻辑"
                },
                "reference_code": "tetris_template",
                "keywords": ["方块", "消除", "下落", "旋转", "经典", "益智", "策略"]
            }
        ]

        for template in templates:
            self.templates[template["id"]] = template

        logger.info(f"加载了 {len(templates)} 个游戏模板")

    async def _preload_templates(self):
        """预加载模板到向量数据库"""
        if not CHROMADB_AVAILABLE:
            return

        try:
            for template_id, template in self.templates.items():
                # 创建文档内容用于embedding
                doc_content = f"""
                游戏名称: {template['name']}
                描述: {template['description']}
                类型: {template['game_type']}
                技术栈: {template['tech_stack']}
                玩法机制: {', '.join(template['mechanics'])}
                关键词: {', '.join(template['keywords'])}
                """

                # 添加到向量数据库
                self.collection.add(
                    documents=[doc_content],
                    metadatas=[{
                        "id": template_id,
                        "name": template['name'],
                        "game_type": template['game_type'],
                        "tech_stack": template['tech_stack']
                    }],
                    ids=[template_id]
                )

            logger.info("模板已添加到向量数据库")

        except Exception as e:
            logger.error(f"预加载模板失败: {e}")

    async def search_templates(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """搜索相似的游戏模板"""
        if not self.is_initialized:
            await self.initialize()

        try:
            if CHROMADB_AVAILABLE and self.collection:
                # 使用向量搜索
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k
                )

                if results['ids'] and results['ids'][0]:
                    return [self.templates[template_id] for template_id in results['ids'][0]]

            # 后备方案：关键词匹配
            matched_templates = []
            query_lower = query.lower()

            for template_id, template in self.templates.items():
                score = 0

                # 检查名称
                if template['name'] in query:
                    score += 5

                # 检查关键词
                for keyword in template['keywords']:
                    if keyword in query_lower:
                        score += 2

                # 检查描述
                for word in query_lower.split():
                    if word in template['description'].lower():
                        score += 1

                if score > 0:
                    matched_templates.append((template, score))

            # 按分数排序
            matched_templates.sort(key=lambda x: x[1], reverse=True)
            return [t[0] for t in matched_templates[:top_k]]

        except Exception as e:
            logger.error(f"搜索模板失败: {e}")
            # 返回默认模板
            return [self.templates.get("snake_game", {})]

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取特定模板"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """获取所有模板"""
        return list(self.templates.values())


# 单例
_template_db: Optional[GameTemplateDB] = None


def get_template_db() -> GameTemplateDB:
    """获取模板数据库单例"""
    global _template_db
    if _template_db is None:
        _template_db = GameTemplateDB()
    return _template_db
