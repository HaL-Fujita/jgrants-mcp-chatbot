#!/usr/bin/env python3.11
"""
JグランツAPIの動作テスト
"""

import requests
import json

def test_search():
    """補助金検索のテスト"""
    print("=== 補助金検索テスト ===")

    url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    params = {
        "keyword": "中小企業",
        "sort": "created_date",
        "order": "DESC",
        "acceptance": 1  # 募集中のみ
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        print(f"✓ API接続成功")
        print(f"✓ 検索結果: {data.get('metadata', {}).get('resultset', {}).get('count', 0)}件")

        # 最初の3件を表示
        results = data.get('result', [])
        for i, subsidy in enumerate(results[:3], 1):
            print(f"\n{i}. {subsidy.get('name', 'N/A')}")
            print(f"   タイトル: {subsidy.get('title', 'N/A')}")
            print(f"   対象地域: {subsidy.get('target_area_search', 'N/A')}")
            print(f"   募集期限: {subsidy.get('acceptance_end_datetime', 'N/A')}")

        return True

    except Exception as e:
        print(f"✗ エラー: {e}")
        return False


def test_detail():
    """補助金詳細取得のテスト"""
    print("\n\n=== 補助金詳細取得テスト ===")

    # まず検索して最初の補助金IDを取得
    url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    params = {
        "keyword": "中小企業",
        "sort": "created_date",
        "order": "DESC"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get('result', [])
        if not results:
            print("✗ テスト用の補助金が見つかりませんでした")
            return False

        subsidy_id = results[0].get('id')
        print(f"補助金ID: {subsidy_id} の詳細を取得中...")

        # 詳細取得
        detail_url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
        detail_response = requests.get(detail_url, timeout=30)
        detail_response.raise_for_status()
        detail_data = detail_response.json()

        if detail_data.get('result'):
            subsidy = detail_data['result'][0] if isinstance(detail_data['result'], list) else detail_data['result']
            print(f"✓ 詳細取得成功")
            print(f"  名称: {subsidy.get('name', 'N/A')}")
            print(f"  補助率: {subsidy.get('subsidy_rate', 'N/A')}")
            print(f"  概要: {subsidy.get('outline', 'N/A')[:100]}...")
            return True
        else:
            print("✗ 詳細情報が取得できませんでした")
            return False

    except Exception as e:
        print(f"✗ エラー: {e}")
        return False


if __name__ == "__main__":
    print("JグランツAPI動作テスト開始\n")

    test1 = test_search()
    test2 = test_detail()

    print("\n\n=== テスト結果 ===")
    print(f"補助金検索: {'✓ 成功' if test1 else '✗ 失敗'}")
    print(f"詳細取得: {'✓ 成功' if test2 else '✗ 失敗'}")

    if test1 and test2:
        print("\n✓ すべてのテストが成功しました！")
    else:
        print("\n✗ 一部のテストが失敗しました")
