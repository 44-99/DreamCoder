"""
MCP工具管理模块 - 管理MCP服务器连接和工具调用
支持文件系统、终端、浏览器等MCP服务器
"""
import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from core.dependencies import logger


class MCPToolManager:
    """MCP工具管理器"""

    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.is_initialized = False

    async def initialize(self):
        """初始化MCP服务器连接"""
        try:
            logger.info("初始化MCP工具管理器")

            # 这里可以连接各种MCP服务器
            # 文件系统MCP、终端MCP、浏览器MCP等
            # 由于MCP协议的复杂性，这里提供基础框架

            self.is_initialized = True
            logger.info("MCP工具管理器初始化完成")
        except Exception as e:
            logger.error(f"MCP初始化失败: {e}")
            self.is_initialized = False

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用MCP工具"""
        if not self.is_initialized:
            logger.warning(f"MCP未初始化，使用本地方法: {tool_name}")
            return await self._call_local_tool(tool_name, arguments)

        try:
            # 实际MCP调用逻辑
            logger.debug(f"调用MCP工具: {server_name}.{tool_name}, 参数: {arguments}")
            # 这里应该实现实际的MCP协议调用
            return await self._call_local_tool(tool_name, arguments)
        except Exception as e:
            logger.error(f"MCP工具调用失败: {e}")
            return {"error": str(e)}

    async def _call_local_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """本地工具实现（当MCP不可用时的后备方案）"""
        try:
            if tool_name == "create_file":
                return self._create_file_local(arguments)
            elif tool_name == "write_file":
                return self._write_file_local(arguments)
            elif tool_name == "read_file":
                return self._read_file_local(arguments)
            elif tool_name == "run_command":
                return await self._run_command_local(arguments)
            elif tool_name == "list_directory":
                return self._list_directory_local(arguments)
            else:
                return {"error": f"未知工具: {tool_name}"}
        except Exception as e:
            logger.error(f"本地工具执行失败: {e}")
            return {"error": str(e)}

    def _create_file_local(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """创建文件"""
        file_path = arguments.get("path")
        content = arguments.get("content", "")

        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"success": True, "path": file_path}
        except Exception as e:
            return {"error": str(e)}

    def _write_file_local(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """写入文件"""
        return self._create_file_local(arguments)

    def _read_file_local(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """读取文件"""
        file_path = arguments.get("path")

        try:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                return {"success": True, "content": content}
            else:
                return {"error": "文件不存在"}
        except Exception as e:
            return {"error": str(e)}

    async def _run_command_local(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """运行命令"""
        command = arguments.get("command")
        cwd = arguments.get("cwd", ".")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            return {
                "success": True,
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore")
            }
        except Exception as e:
            return {"error": str(e)}

    def _list_directory_local(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """列出目录"""
        directory = arguments.get("path", ".")

        try:
            path = Path(directory)
            if path.is_dir():
                items = []
                for item in path.iterdir():
                    items.append({
                        "name": item.name,
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })
                return {"success": True, "items": items}
            else:
                return {"error": "不是目录"}
        except Exception as e:
            return {"error": str(e)}

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        return [
            {
                "name": "create_file",
                "description": "创建文件并写入内容",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}
            },
            {
                "name": "write_file",
                "description": "写入文件内容",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}
            },
            {
                "name": "read_file",
                "description": "读取文件内容",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}
            },
            {
                "name": "run_command",
                "description": "运行shell命令",
                "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "cwd": {"type": "string"}}}
            },
            {
                "name": "list_directory",
                "description": "列出目录内容",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}
            }
        ]

    async def close(self):
        """关闭所有MCP连接"""
        for server_name, session in self.sessions.items():
            try:
                logger.info(f"关闭MCP服务器连接: {server_name}")
                # 这里应该实现实际的关闭逻辑
            except Exception as e:
                logger.error(f"关闭MCP连接失败: {e}")

        self.sessions.clear()
        self.is_initialized = False


# 单例
_mcp_manager: Optional[MCPToolManager] = None


def get_mcp_manager() -> MCPToolManager:
    """获取MCP管理器单例"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPToolManager()
    return _mcp_manager
