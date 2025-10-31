"""
LLM統合モジュール（Claude API + OpenAI API）
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI
from .jgrants import search_subsidies, get_subsidy_detail, search_active_subsidies

# 環境変数の読み込み
load_dotenv()

# LLMクライアントの初期化
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ツール定義（Function Calling用）
TOOLS_DEFINITION = [
    {
        "name": "search_subsidies",
        "description": "Jグランツで補助金を検索します。キーワードで検索し、募集中のみや地域でフィルタリングできます。",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "検索キーワード（2～255文字）"
                },
                "acceptance": {
                    "type": "integer",
                    "description": "募集中フィルタ（1: 募集中のみ, 0: 全て）",
                    "enum": [0, 1]
                },
                "target_area": {
                    "type": "string",
                    "description": "対象地域（例: 東京都、大阪府など）"
                },
                "sort": {
                    "type": "string",
                    "description": "ソート項目",
                    "enum": ["created_date", "acceptance_start_datetime", "acceptance_end_datetime"]
                },
                "order": {
                    "type": "string",
                    "description": "ソート順",
                    "enum": ["ASC", "DESC"]
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "get_subsidy_detail",
        "description": "補助金IDを指定して詳細情報を取得します。補助率、概要、注意事項などの詳細が取得できます。",
        "parameters": {
            "type": "object",
            "properties": {
                "subsidy_id": {
                    "type": "string",
                    "description": "補助金ID（search_subsidiesで取得したID）"
                }
            },
            "required": ["subsidy_id"]
        }
    },
    {
        "name": "search_active_subsidies",
        "description": "現在募集中の補助金を検索します。申請期限が近い順に表示します。",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "検索キーワード"
                },
                "target_area": {
                    "type": "string",
                    "description": "対象地域（例: 東京都、大阪府など）"
                }
            },
            "required": ["keyword"]
        }
    }
]


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """
    ツールを実行して結果を返す
    """
    if tool_name == "search_subsidies":
        result = search_subsidies(
            keyword=tool_args["keyword"],
            sort=tool_args.get("sort", "created_date"),
            order=tool_args.get("order", "DESC"),
            acceptance=tool_args.get("acceptance"),
            target_area_search=tool_args.get("target_area")
        )
    elif tool_name == "get_subsidy_detail":
        result = get_subsidy_detail(tool_args["subsidy_id"])
    elif tool_name == "search_active_subsidies":
        result = search_active_subsidies(
            keyword=tool_args["keyword"],
            target_area=tool_args.get("target_area")
        )
    else:
        result = {"error": f"Unknown tool: {tool_name}", "success": False}

    return json.dumps(result, ensure_ascii=False, indent=2)


async def chat_with_claude(
    messages: List[Dict[str, str]],
    max_iterations: int = 5
) -> Dict[str, Any]:
    """
    Claude APIを使用してチャット処理

    Args:
        messages: チャット履歴 [{"role": "user", "content": "..."}]
        max_iterations: ツール呼び出しの最大反復回数

    Returns:
        レスポンス辞書
    """
    try:
        # Claudeのツール定義形式に変換
        claude_tools = []
        for tool in TOOLS_DEFINITION:
            claude_tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            })

        current_messages = messages.copy()
        iterations = 0

        while iterations < max_iterations:
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                tools=claude_tools,
                messages=current_messages
            )

            # ツール呼び出しがない場合は終了
            if response.stop_reason != "tool_use":
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text

                return {
                    "success": True,
                    "model": "claude",
                    "response": final_text,
                    "tool_calls": []
                }

            # ツール呼び出しを処理
            tool_calls_info = []
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    tool_call_id = block.id

                    # ツール実行
                    tool_result = execute_tool(tool_name, tool_args)

                    tool_calls_info.append({
                        "name": tool_name,
                        "arguments": tool_args,
                        "result": json.loads(tool_result)
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call_id,
                        "content": tool_result
                    })

            # メッセージ履歴を更新
            current_messages.append({
                "role": "assistant",
                "content": response.content
            })
            current_messages.append({
                "role": "user",
                "content": tool_results
            })

            iterations += 1

        return {
            "success": False,
            "error": "最大反復回数に達しました",
            "model": "claude"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Claude API error: {str(e)}",
            "model": "claude"
        }


async def chat_with_openai(
    messages: List[Dict[str, str]],
    max_iterations: int = 5
) -> Dict[str, Any]:
    """
    OpenAI APIを使用してチャット処理

    Args:
        messages: チャット履歴 [{"role": "user", "content": "..."}]
        max_iterations: ツール呼び出しの最大反復回数

    Returns:
        レスポンス辞書
    """
    try:
        # OpenAIのツール定義形式に変換
        openai_tools = []
        for tool in TOOLS_DEFINITION:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })

        current_messages = messages.copy()
        iterations = 0

        while iterations < max_iterations:
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=current_messages,
                tools=openai_tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # ツール呼び出しがない場合は終了
            if not message.tool_calls:
                return {
                    "success": True,
                    "model": "openai",
                    "response": message.content or "",
                    "tool_calls": []
                }

            # ツール呼び出しを処理
            tool_calls_info = []
            current_messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # ツール実行
                tool_result = execute_tool(tool_name, tool_args)

                tool_calls_info.append({
                    "name": tool_name,
                    "arguments": tool_args,
                    "result": json.loads(tool_result)
                })

                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

            iterations += 1

        return {
            "success": False,
            "error": "最大反復回数に達しました",
            "model": "openai"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"OpenAI API error: {str(e)}",
            "model": "openai"
        }


async def chat_with_both(
    messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Claude と OpenAI の両方に並列でリクエストを送信

    Args:
        messages: チャット履歴

    Returns:
        両方のレスポンスを含む辞書
    """
    claude_task = chat_with_claude(messages)
    openai_task = chat_with_openai(messages)

    claude_result, openai_result = await asyncio.gather(
        claude_task, openai_task, return_exceptions=True
    )

    # 例外処理
    if isinstance(claude_result, Exception):
        claude_result = {
            "success": False,
            "error": str(claude_result),
            "model": "claude"
        }

    if isinstance(openai_result, Exception):
        openai_result = {
            "success": False,
            "error": str(openai_result),
            "model": "openai"
        }

    return {
        "claude": claude_result,
        "openai": openai_result
    }
