"""
ASO 关键词优化监控工具
监控 App Store 关键词排名变化、竞品动态、评分趋势
"""
import requests
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36",
}

APP_IDS = {
    "jielingqi": "",
    "maoshangyouqian": "",
    "qingyuhongmao": "",
}

ASO_KEYWORDS = {
    "jielingqi": ["青少年心理", "AI陪伴", "亲子沟通", "情绪管理", "育儿助手", "心理咨询App"],
    "maoshangyouqian": ["宠物服务", "撸猫平台", "宠物预约", "铲屎官", "宠物社交App"],
    "qingyuhongmao": ["数字遗嘱", "资产传承", "数字遗产", "遗嘱App", "信息守护"],
}

_ranking_history = {}


def search_appstore_keyword(keyword: str, country: str = "cn") -> list:
    """搜索 App Store 关键词，返回前10个结果"""
    results = []
    try:
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(keyword)}&country={country}&media=software&limit=10&lang=zh_cn"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        for i, app in enumerate(data.get("results", [])):
            results.append({
                "rank": i + 1,
                "app_id": str(app.get("trackId", "")),
                "name": app.get("trackName", ""),
                "developer": app.get("artistName", ""),
                "rating": app.get("averageUserRating", 0),
                "rating_count": app.get("userRatingCount", 0),
                "price": app.get("price", 0),
                "icon_url": app.get("artworkUrl60", ""),
            })
    except Exception as e:
        print(f"ASO搜索失败 [{keyword}]: {e}")
    return results


def get_app_ranking_for_keyword(keyword: str, app_id: str, country: str = "cn") -> int:
    """获取指定 App 在某关键词下的排名，未找到返回 -1"""
    results = search_appstore_keyword(keyword, country)
    for item in results:
        if item["app_id"] == str(app_id):
            return item["rank"]
    return -1


def monitor_all_keywords() -> dict:
    """监控所有产品的关键词排名"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = {"checked_at": timestamp, "products": {}}
    for product_id, app_id in APP_IDS.items():
        keywords = ASO_KEYWORDS.get(product_id, [])
        kw_results = []
        for kw in keywords:
            results = search_appstore_keyword(kw)
            own_rank = -1
            if app_id:
                for r in results:
                    if r["app_id"] == app_id:
                        own_rank = r["rank"]
                        break
            kw_results.append({
                "keyword": kw,
                "own_rank": own_rank,
                "top3_competitors": [r["name"] for r in results[:3]],
            })
        report["products"][product_id] = {
            "app_id": app_id,
            "keywords": kw_results,
        }
        _ranking_history.setdefault(product_id, []).append({
            "time": timestamp,
            "keywords": kw_results,
        })
    return report


def get_keyword_suggestions(product_id: str) -> list:
    """根据现有关键词搜索结果，建议新关键词"""
    base_keywords = ASO_KEYWORDS.get(product_id, [])
    suggestions = []
    for kw in base_keywords[:3]:
        results = search_appstore_keyword(kw)
        for app in results[:5]:
            name_words = app["name"].replace("-", " ").replace("·", " ").split()
            for w in name_words:
                if len(w) >= 2 and w not in base_keywords and w not in suggestions:
                    suggestions.append(w)
    return suggestions[:15]


def get_history(product_id: str) -> list:
    return _ranking_history.get(product_id, [])
