#!/usr/bin/env python3.11
"""
Jグランツ（補助金電子申請システム）のAPIをMCP経由で利用可能にするサーバー

このサーバーは、デジタル庁が運営するJグランツの公開APIをラップし、
生成AIから補助金情報を検索・取得できるようにします。
"""

import asyncio
import json
import requests
from typing import Optional, Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# JグランツAPIのベースURL
JGRANTS_API_BASE = "https://api.jgrants-portal.go.jp/exp/v1/public"

# MCPサーバーの初期化
server = Server("jgrants-subsidy-search")


def search_subsidies_api(
    keyword: str,
    sort: str = "created_date",
    order: str = "DESC",
    acceptance: Optional[int] = None,
    target_area_search: Optional[str] = None,
    target_number_of_employees: Optional[str] = None,
    use_purpose: Optional[str] = None,
    industry: Optional[str] = None
) -> dict:
    """
    Jグランツで補助金を検索します

    Args:
        keyword: 検索キーワード（2～255文字）。大文字・小文字や全角・半角の表記ゆれを許容
        sort: ソート項目（created_date, acceptance_start_datetime, acceptance_end_datetime）
        order: ソート順（ASC: 昇順, DESC: 降順）
        acceptance: 募集期間内フィルタ（1: 募集中のみ, 0 or None: 全て）
        target_area_search: 対象地域（都道府県名など）
        target_number_of_employees: 従業員数要件
        use_purpose: 利用目的（複数の場合は「 / 」で区切る）
        industry: 業種（複数の場合は「 / 」で区切る）

    Returns:
        補助金情報のリスト（JSON形式）
    """

    # 必須パラメータのバリデーション
    if not keyword or len(keyword) < 2 or len(keyword) > 255:
        return {
            "error": "keywordは2～255文字で指定してください",
            "success": False
        }

    if sort not in ["created_date", "acceptance_start_datetime", "acceptance_end_datetime"]:
        return {
            "error": "sortはcreated_date, acceptance_start_datetime, acceptance_end_datetimeのいずれかを指定してください",
            "success": False
        }

    if order not in ["ASC", "DESC"]:
        return {
            "error": "orderはASCまたはDESCを指定してください",
            "success": False
        }

    # APIリクエストパラメータの構築
    params = {
        "keyword": keyword,
        "sort": sort,
        "order": order
    }

    # オプションパラメータの追加
    if acceptance is not None:
        params["acceptance"] = acceptance
    if target_area_search:
        params["target_area_search"] = target_area_search
    if target_number_of_employees:
        params["target_number_of_employees"] = target_number_of_employees
    if use_purpose:
        params["use_purpose"] = use_purpose
    if industry:
        params["industry"] = industry

    try:
        # JグランツAPIへのリクエスト
        url = f"{JGRANTS_API_BASE}/subsidies"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # 結果の整形
        result = {
            "success": True,
            "count": data.get("metadata", {}).get("resultset", {}).get("count", 0),
            "subsidies": []
        }

        # 補助金情報を見やすく整形
        for subsidy in data.get("result", []):
            result["subsidies"].append({
                "id": subsidy.get("id"),
                "name": subsidy.get("name"),
                "title": subsidy.get("title"),
                "target_area": subsidy.get("target_area_search"),
                "subsidy_max_limit": subsidy.get("subsidy_max_limit"),
                "acceptance_start": subsidy.get("acceptance_start_datetime"),
                "acceptance_end": subsidy.get("acceptance_end_datetime"),
                "target_employees": subsidy.get("target_number_of_employees")
            })

        return result

    except requests.exceptions.RequestException as e:
        return {
            "error": f"API通信エラー: {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"予期しないエラー: {str(e)}",
            "success": False
        }


def get_subsidy_detail_api(subsidy_id: str) -> dict:
    """
    補助金の詳細情報を取得します

    Args:
        subsidy_id: 補助金ID（search_subsidiesで取得したID）

    Returns:
        補助金の詳細情報（JSON形式）
    """

    if not subsidy_id:
        return {
            "error": "subsidy_idを指定してください",
            "success": False
        }

    try:
        # JグランツAPIへのリクエスト
        url = f"{JGRANTS_API_BASE}/subsidies/id/{subsidy_id}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if not data.get("result"):
            return {
                "error": "指定されたIDの補助金が見つかりませんでした",
                "success": False
            }

        subsidy = data["result"][0] if isinstance(data["result"], list) else data["result"]

        # 詳細情報を整形（ファイルのbase64データは除外して見やすくする）
        result = {
            "success": True,
            "subsidy": {
                "id": subsidy.get("id"),
                "name": subsidy.get("name"),
                "title": subsidy.get("title"),
                "target_area": subsidy.get("target_area_search"),
                "subsidy_max_limit": subsidy.get("subsidy_max_limit"),
                "subsidy_rate": subsidy.get("subsidy_rate"),
                "acceptance_start": subsidy.get("acceptance_start_datetime"),
                "acceptance_end": subsidy.get("acceptance_end_datetime"),
                "target_employees": subsidy.get("target_number_of_employees"),
                "purpose": subsidy.get("purpose"),
                "outline": subsidy.get("outline"),
                "note": subsidy.get("note"),
                "grant_guideline_url": subsidy.get("grant_guideline_url"),
                "application_form_files": len(subsidy.get("application_form_files", [])) if subsidy.get("application_form_files") else 0
            }
        }

        return result

    except requests.exceptions.RequestException as e:
        return {
            "error": f"API通信エラー: {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"予期しないエラー: {str(e)}",
            "success": False
        }


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    MCPクライアントが利用可能なツールのリストを返す
    """
    return [
        Tool(
            name="search_subsidies",
            description="Jグランツで補助金を検索します。キーワードで検索し、募集中のみや地域でフィルタリングできます。",
            inputSchema={
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
                        "enum": ["created_date", "acceptance_start_datetime", "acceptance_end_datetime"],
                        "default": "created_date"
                    },
                    "order": {
                        "type": "string",
                        "description": "ソート順",
                        "enum": ["ASC", "DESC"],
                        "default": "DESC"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_subsidy_detail",
            description="補助金IDを指定して詳細情報を取得します。補助率、概要、注意事項などの詳細が取得できます。",
            inputSchema={
                "type": "object",
                "properties": {
                    "subsidy_id": {
                        "type": "string",
                        "description": "補助金ID（search_subsidiesで取得したID）"
                    }
                },
                "required": ["subsidy_id"]
            }
        ),
        Tool(
            name="search_active_subsidies",
            description="現在募集中の補助金を検索します（便利関数）。申請期限が近い順に表示します。",
            inputSchema={
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
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    MCPクライアントからのツール呼び出しを処理する
    """
    if name == "search_subsidies":
        result = search_subsidies_api(
            keyword=arguments["keyword"],
            sort=arguments.get("sort", "created_date"),
            order=arguments.get("order", "DESC"),
            acceptance=arguments.get("acceptance"),
            target_area_search=arguments.get("target_area")
        )
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    elif name == "get_subsidy_detail":
        result = get_subsidy_detail_api(arguments["subsidy_id"])
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    elif name == "search_active_subsidies":
        result = search_subsidies_api(
            keyword=arguments["keyword"],
            acceptance=1,
            target_area_search=arguments.get("target_area"),
            sort="acceptance_end_datetime",
            order="ASC"
        )
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """
    MCPサーバーのメイン関数
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="jgrants-subsidy-search",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
