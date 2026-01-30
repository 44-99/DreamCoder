"""统一模型测试脚本 - 支持通过环境变量选择不同的LLM提供商"""
import os
from pathlib import Path
from dotenv import dotenv_values, load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量 - 从backend目录加载
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"

# 清除可能缓存的旧环境变量
for key in list(os.environ.keys()):
    if 'API_KEY' in key or 'LLM' in key:
        del os.environ[key]

# 直接从文件读取环境变量值
env_values = dotenv_values(env_path)

# 更新到 os.environ
for key, value in env_values.items():
    os.environ[key] = value

# LLM提供商选择
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# 代码生成温度参数
CODE_GEN_TEMP = float(os.getenv("CODE_GEN_TEMPERATURE", "0.0"))

print("=" * 60)
print(f"LLM 提供商: {LLM_PROVIDER.upper()}")
print(f"代码生成温度: {CODE_GEN_TEMP}")
print("=" * 60)


def get_llm():
    """根据环境变量选择LLM提供商"""
    if LLM_PROVIDER == "deepseek":
        # DeepSeek 使用 OpenAI 兼容的 API
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    elif LLM_PROVIDER == "qwen":
        # 通义千问 (阿里云)
        api_key = os.getenv("QWEN_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        model = os.getenv("QWEN_MODEL", "qwen-plus")
    else:
        # 默认使用 OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    print(f"API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")
    print(f"Base URL: {base_url}")
    print(f"模型: {model}")
    return ChatOpenAI(
        model=model,
        temperature=CODE_GEN_TEMP,
        openai_api_key=api_key,
        openai_api_base=base_url
    )


async def test_basic_chat():
    """测试1: 基础对话"""
    print("\n" + "-" * 60)
    print("测试 1: 基础对话")
    print("-" * 60)

    try:
        llm = get_llm()
        response = await llm.ainvoke("你好！请用一句话简单介绍一下你自己。")
        print(f"[OK] 回复: {response.content[:100]}...")
        return True

    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False


async def test_code_generation():
    """测试2: 代码生成"""
    print("\n" + "-" * 60)
    print("测试 2: 代码生成")
    print("-" * 60)

    try:
        llm = get_llm()
        response = await llm.ainvoke("用Python写一个简单的冒泡排序函数，并添加注释。")
        print(f"[OK] 生成了 {len(response.content)} 字符的代码")
        # 显示前300个字符
        print(f"代码片段: {response.content[:300]}...")
        return True

    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False


async def test_json_output():
    """测试3: JSON 结构化输出"""
    print("\n" + "-" * 60)
    print("测试 3: JSON 结构化输出")
    print("-" * 60)

    try:
        from pydantic import BaseModel, Field
        from typing import List

        class GameInfo(BaseModel):
            """游戏信息"""
            game_name: str = Field(description="游戏名称")
            genre: str = Field(description="游戏类型")
            mechanics: List[str] = Field(description="核心玩法机制")

        # DeepSeek 不支持 response_format，使用 JSON 提示替代
        if LLM_PROVIDER != "openai":
            print("[INFO] 国产模型不支持 response_format，使用 JSON 提示替代")

            prompt = """请以 JSON 格式返回贪吃蛇游戏的基本信息，格式如下：
{
    "game_name": "游戏名称",
    "genre": "游戏类型",
    "mechanics": ["核心玩法机制1", "核心玩法机制2"]
}

只返回 JSON，不要有其他说明文字。"""

            llm = get_llm()
            response = await llm.ainvoke(prompt)

            # 解析 JSON 响应
            import json
            content = response.content.strip()

            # 提取 JSON 部分（如果有 markdown 代码块）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result_data = json.loads(content)

            print(f"[OK] 游戏名称: {result_data['game_name']}")
            print(f"[OK] 游戏类型: {result_data['genre']}")
            print(f"[OK] 核心机制: {', '.join(result_data['mechanics'])}")
            return True
        else:
            # 其他提供商使用结构化输出
            llm = get_llm()
            structured_llm = llm.with_structured_output(GameInfo)
            result = await structured_llm.ainvoke("贪吃蛇游戏的基本信息是什么？")

            print(f"[OK] 游戏名称: {result.game_name}")
            print(f"[OK] 游戏类型: {result.genre}")
            print(f"[OK] 核心机制: {', '.join(result.mechanics)}")
            return True

    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n开始测试 LLM 模型...")

    results = {
        "基础对话": await test_basic_chat(),
        "代码生成": await test_code_generation(),
        "JSON输出": await test_json_output(),
    }

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[OK] 通过" if passed else "[FAIL] 失败"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n[所有测试通过] 模型配置正确，可以正常使用！")
    else:
        print("\n[部分测试失败] 请检查配置和网络连接。")

    return all_passed


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
