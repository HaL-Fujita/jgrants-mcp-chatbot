"""
Jグランツ API連携モジュール
"""
import requests
from typing import Optional, Dict, Any, List

# JグランツAPIのベースURL
JGRANTS_API_BASE = "https://api.jgrants-portal.go.jp/exp/v1/public"


def search_subsidies(
    keyword: str,
    sort: str = "created_date",
    order: str = "DESC",
    acceptance: Optional[int] = None,
    target_area_search: Optional[str] = None,
    target_number_of_employees: Optional[str] = None,
    use_purpose: Optional[str] = None,
    industry: Optional[str] = None
) -> Dict[str, Any]:
    """
    Jグランツで補助金を検索します

    Args:
        keyword: 検索キーワード（2～255文字）
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


def get_subsidy_detail(subsidy_id: str) -> Dict[str, Any]:
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


def search_active_subsidies(
    keyword: str,
    target_area: Optional[str] = None
) -> Dict[str, Any]:
    """
    現在募集中の補助金を検索します（便利関数）
    申請期限が近い順に表示

    Args:
        keyword: 検索キーワード
        target_area: 対象地域

    Returns:
        募集中の補助金情報（申請期限が近い順）
    """
    return search_subsidies(
        keyword=keyword,
        acceptance=1,
        target_area_search=target_area,
        sort="acceptance_end_datetime",
        order="ASC"
    )
