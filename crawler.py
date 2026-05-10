import requests
import json
import re
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

def parse_hot_value(hot_value):
    """解析热度值，支持数字和带单位的字符串"""
    if isinstance(hot_value, (int, float)):
        return int(hot_value)
    if isinstance(hot_value, str):
        # 处理带中文单位的热度值，如 "742 万热度"
        hot_value = hot_value.replace(",", "")
        match = re.search(r'([\d.]+)', hot_value)
        if match:
            value = float(match.group(1))
            if "万" in hot_value:
                value *= 10000
            return int(value)
    return 0

def fetch_platform_hot(api_type, platform_name):
    """使用聚合API采集指定平台的热点"""
    results = []
    try:
        url = f"https://uapis.cn/api/v1/misc/hotboard?type={api_type}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()

        # API返回的数据结构：{"type": "weibo", "update_time": "...", "list": [...]}
        items = data.get("list", [])
        for item in items[:20]:
            keyword = item.get("title", "")
            hot_value = parse_hot_value(item.get("hot_value", 0))
            if keyword:
                results.append({
                    "rank": item.get("index", 0),
                    "keyword": keyword,
                    "hot_value": hot_value,
                    "platform": platform_name,
                    "category": ""
                })
        print(f"{platform_name}采集成功: {len(results)}条")
    except Exception as e:
        print(f"{platform_name}采集失败: {e}")
    return results

def fetch_weibo_hot():
    return fetch_platform_hot("weibo", "微博")

def fetch_zhihu_hot():
    return fetch_platform_hot("zhihu", "知乎")

def fetch_baidu_hot():
    return fetch_platform_hot("baidu", "百度")

def fetch_douyin_hot():
    results = []
    try:
        url = "https://aweme.snssdk.com/aweme/v1/hot/search/list/"
        params = {"device_platform": "webapp", "aid": 1340, "channel": "channel_pc_web"}
        headers = {**HEADERS, "Referer": "https://www.douyin.com/"}
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("word_list", [])
        for i, item in enumerate(items[:20]):
            word = item.get("word", "")
            if word:
                results.append({"rank": i+1, "keyword": word, "hot_value": item.get("hot_value", 0), "platform": "抖音", "category": ""})
        print(f"抖音采集成功: {len(results)}条")
    except Exception as e:
        print(f"抖音采集失败: {e}")
    return results

def fetch_toutiao_hot():
    results = []
    try:
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        h = {**HEADERS, "Referer": "https://www.toutiao.com/"}
        resp = requests.get(url, headers=h, timeout=10)
        data = resp.json()
        for i, item in enumerate(data.get("data", [])[:20]):
            title = item.get("Title", "")
            if title:
                hot_value = parse_hot_value(item.get("HotValue", 0))
                results.append({"rank": i+1, "keyword": title, "hot_value": hot_value, "platform": "头条", "category": ""})
        print(f"头条采集成功: {len(results)}条")
    except Exception as e:
        print(f"头条采集失败: {e}")
    return results

def fetch_all_hotspots():
    all_items = []
    print("正在采集微博热搜...")
    all_items.extend(fetch_weibo_hot())
    print("正在采集知乎热榜...")
    all_items.extend(fetch_zhihu_hot())
    print("正在采集百度热搜...")
    all_items.extend(fetch_baidu_hot())
    print("正在采集抖音热榜...")
    all_items.extend(fetch_douyin_hot())
    print("正在采集头条热榜...")
    all_items.extend(fetch_toutiao_hot())
    return {"collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "total": len(all_items), "items": all_items}

if __name__ == "__main__":
    result = fetch_all_hotspots()
    print(json.dumps(result, ensure_ascii=False, indent=2))