import os, sys, json
from datetime import datetime
from flask import Flask, render_template, jsonify, request

sys.path.insert(0, os.path.dirname(__file__))
from crawler import fetch_all_hotspots
from matcher import analyze_hotspots, PRODUCTS
from copywriter import generate_all_copies, PLATFORM_PROMPTS
from scheduler import add_scheduled_post, get_all_posts, update_post_status, delete_post, get_posts_by_platform, get_posts_by_status, batch_update_posts
from publisher import get_login_status, publish_post, batch_publish_jichuang
import threading
import subprocess
from asset_generator import generate_qrcode_base64, generate_poster_text, generate_video_script, generate_aso_keywords
from aso_monitor import monitor_all_keywords, get_keyword_suggestions, search_appstore_keyword, ASO_KEYWORDS
from crm import (add_contact, get_contacts, create_campaign, get_campaigns,
                 send_campaign, get_send_logs, create_recall_campaign, RECALL_TEMPLATES)
from platform_rules import get_platform_rules, validate_content, get_optimal_posting_time

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "promotion-2026")

_hotspot_cache = {"data": None, "ts": None}


def get_cached_hotspots(force=False):
    global _hotspot_cache
    now = datetime.now()
    if not force and _hotspot_cache["data"] and _hotspot_cache["ts"]:
        if (now - _hotspot_cache["ts"]).seconds < 7200:
            return _hotspot_cache["data"]
    raw = fetch_all_hotspots()
    # 确保原始数据中的平台名称是正确的中文
    raw_items = raw.get("items", [])
    for item in raw_items:
        platform = item.get("platform", "")
        if isinstance(platform, str):
            # 确保平台名称是中文
            if platform == "weibo":
                item["platform"] = "微博"
            elif platform == "zhihu":
                item["platform"] = "知乎"
            elif platform == "baidu":
                item["platform"] = "百度"
            elif platform == "toutiao":
                item["platform"] = "头条"
            elif platform == "douyin":
                item["platform"] = "抖音"
            elif platform == "xiaohongshu":
                item["platform"] = "小红书"
    analyzed = analyze_hotspots(raw_items)
    # 确保分析后的数据中的平台名称也是正确的中文
    for item in analyzed:
        platform = item.get("platform", "")
        if isinstance(platform, str):
            # 确保平台名称是中文
            if platform == "weibo":
                item["platform"] = "微博"
            elif platform == "zhihu":
                item["platform"] = "知乎"
            elif platform == "baidu":
                item["platform"] = "百度"
            elif platform == "toutiao":
                item["platform"] = "头条"
            elif platform == "douyin":
                item["platform"] = "抖音"
            elif platform == "xiaohongshu":
                item["platform"] = "小红书"
    result = {**raw, "items": analyzed, "total": len(analyzed)}  # 更新total值
    _hotspot_cache = {"data": result, "ts": now}
    return result


# ─── Pages ────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS, platforms=PLATFORM_PROMPTS)

@app.route("/copywriter")
def page_copywriter():
    return render_template("copywriter.html", products=PRODUCTS, platforms=PLATFORM_PROMPTS)

@app.route("/publisher")
def page_publisher():
    return render_template("publisher.html", products=PRODUCTS, platforms=PLATFORM_PROMPTS)

@app.route("/assets")
def page_assets():
    return render_template("assets.html", products=PRODUCTS)

@app.route("/aso")
def page_aso():
    return render_template("aso.html", products=PRODUCTS, aso_keywords=ASO_KEYWORDS)

@app.route("/crm")
def page_crm():
    return render_template("crm.html", products=PRODUCTS, recall_templates=RECALL_TEMPLATES)

@app.route("/dashboard")
def page_dashboard():
    return render_template("dashboard.html", products=PRODUCTS)

# ─── Hotspot API ──────────────────────────────────────────
@app.route("/api/hotspots")
def api_hotspots():
    try:
        return jsonify({"success": True, "data": get_cached_hotspots()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/hotspots/refresh")
def api_hotspots_refresh():
    try:
        return jsonify({"success": True, "data": get_cached_hotspots(force=True)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ─── Copywriter API ───────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
def api_generate():
    body = request.json or {}
    keyword = body.get("keyword", "")
    product_id = body.get("product_id", "")
    platforms = body.get("platforms") or list(PLATFORM_PROMPTS.keys())
    hot_value = body.get("hot_value", 0)
    if not keyword or product_id not in PRODUCTS:
        return jsonify({"success": False, "error": "缺少 keyword 或无效 product_id"})
    try:
        copies = generate_all_copies(keyword, product_id, hot_value, platforms)
        return jsonify({"success": True, "keyword": keyword,
                        "product_name": PRODUCTS[product_id]["name"], "copies": copies})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ─── Scheduler / Publisher API ────────────────────────────
@app.route("/api/posts", methods=["GET"])
def api_posts_list():
    return jsonify({"success": True, "data": get_all_posts()})

@app.route("/api/posts", methods=["POST"])
def api_posts_create():
    body = request.json or {}
    post = add_scheduled_post(
        keyword=body.get("keyword", ""),
        product_id=body.get("product_id", ""),
        platform_id=body.get("platform_id", ""),
        content=body.get("content", ""),
        scheduled_time_str=body.get("scheduled_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    return jsonify({"success": True, "data": post})

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def api_posts_delete(post_id):
    delete_post(post_id)
    return jsonify({"success": True})

@app.route("/api/posts/<int:post_id>/status", methods=["PUT"])
def api_posts_status(post_id):
    status = (request.json or {}).get("status", "")
    update_post_status(post_id, status)
    return jsonify({"success": True})

@app.route("/api/login-status")
def api_login_status():
    return jsonify({"success": True, "data": get_login_status()})

@app.route("/api/publish", methods=["POST"])
def api_publish():
    body = request.json or {}
    platform_id = body.get("platform_id", "")
    content = body.get("content", "")
    title = body.get("title", "")
    if not platform_id or not content:
        return jsonify({"success": False, "error": "缺少 platform_id 或 content"})
    try:
        result = publish_post({"platform_id": platform_id, "content": content, "title": title})
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/publish/batch-jichuang", methods=["POST"])
def api_batch_publish_jichuang():
    """智能批量发布到即创平台"""
    try:
        result = batch_publish_jichuang()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 全局变量，用于跟踪自动化流程状态
auto_publish_status = {
    "running": False,
    "start_time": None,
    "log": []
}

def run_auto_publish():
    """在后台线程中运行自动化流程"""
    global auto_publish_status
    auto_publish_status["running"] = True
    auto_publish_status["start_time"] = datetime.now()
    auto_publish_status["log"] = []
    
    try:
        import sys
        import os
        script_path = os.path.join(os.path.dirname(__file__), "auto_publish.py")
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        for line in process.stdout:
            auto_publish_status["log"].append(line.rstrip())
            if len(auto_publish_status["log"]) > 100:
                auto_publish_status["log"] = auto_publish_status["log"][-100:]
        
        process.wait()
        
    except Exception as e:
        auto_publish_status["log"].append(f"❌ 自动化流程出错: {str(e)}")
    
    auto_publish_status["running"] = False

@app.route("/api/auto-publish/start", methods=["POST"])
def api_start_auto_publish():
    """启动完全自动化发布流程"""
    global auto_publish_status
    if auto_publish_status["running"]:
        return jsonify({"success": False, "error": "自动化流程已经在运行中"})
    
    thread = threading.Thread(target=run_auto_publish, daemon=True)
    thread.start()
    
    return jsonify({"success": True, "message": "自动化流程已启动"})

@app.route("/api/auto-publish/status", methods=["GET"])
def api_auto_publish_status():
    """获取自动化流程状态"""
    global auto_publish_status
    return jsonify(auto_publish_status)

# ─── Platform Rules API ─────────────────────────────────────
@app.route("/api/platform-rules/<platform_id>")
def api_platform_rules(platform_id):
    rules = get_platform_rules(platform_id)
    return jsonify({"success": True, "data": rules})

@app.route("/api/validate-content", methods=["POST"])
def api_validate_content():
    body = request.json or {}
    platform_id = body.get("platform_id", "")
    content = body.get("content", "")
    if not platform_id or not content:
        return jsonify({"success": False, "error": "缺少 platform_id 或 content"})
    result = validate_content(platform_id, content)
    return jsonify({"success": True, "data": result})

@app.route("/api/optimal-posting-times/<platform_id>")
def api_optimal_posting_times(platform_id):
    times = get_optimal_posting_time(platform_id)
    return jsonify({"success": True, "data": times})

# ─── Enhanced Scheduler API ─────────────────────────────────
@app.route("/api/posts/platform/<platform_id>")
def api_posts_by_platform(platform_id):
    posts = get_posts_by_platform(platform_id)
    return jsonify({"success": True, "data": posts})

@app.route("/api/posts/status/<status>")
def api_posts_by_status(status):
    posts = get_posts_by_status(status)
    return jsonify({"success": True, "data": posts})

@app.route("/api/posts/batch-update", methods=["PUT"])
def api_posts_batch_update():
    body = request.json or {}
    post_ids = body.get("post_ids", [])
    status = body.get("status", "")
    if not post_ids or not status:
        return jsonify({"success": False, "error": "缺少 post_ids 或 status"})
    updated = batch_update_posts(post_ids, status)
    return jsonify({"success": True, "updated": updated})

# ─── Asset Generator API ──────────────────────────────────
@app.route("/api/assets/qrcode", methods=["POST"])
def api_qrcode():
    body = request.json or {}
    url = body.get("url", "https://qingguoguang.com")
    qr_b64 = generate_qrcode_base64(url)
    return jsonify({"success": True, "qrcode_base64": qr_b64, "url": url})

@app.route("/api/assets/poster", methods=["POST"])
def api_poster():
    body = request.json or {}
    poster = generate_poster_text(
        product_id=body.get("product_id", "jielingqi"),
        headline=body.get("headline", ""),
        subtext=body.get("subtext", ""),
        hotspot=body.get("hotspot", ""),
    )
    return jsonify({"success": True, "data": poster})

@app.route("/api/assets/video-script", methods=["POST"])
def api_video_script():
    body = request.json or {}
    product_id = body.get("product_id", "jielingqi")
    keyword = body.get("keyword", "热点")
    if product_id not in PRODUCTS:
        return jsonify({"success": False, "error": "无效 product_id"})
    script = generate_video_script(keyword, product_id, PRODUCTS[product_id])
    return jsonify({"success": True, "data": script})

@app.route("/api/assets/aso-keywords", methods=["POST"])
def api_aso_keywords():
    body = request.json or {}
    product_id = body.get("product_id", "jielingqi")
    if product_id not in PRODUCTS:
        return jsonify({"success": False, "error": "无效 product_id"})
    result = generate_aso_keywords(product_id, PRODUCTS[product_id])
    return jsonify({"success": True, "data": result})

# ─── ASO Monitor API ──────────────────────────────────────
@app.route("/api/aso/monitor")
def api_aso_monitor():
    try:
        report = monitor_all_keywords()
        return jsonify({"success": True, "data": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/aso/search", methods=["POST"])
def api_aso_search():
    body = request.json or {}
    keyword = body.get("keyword", "")
    if not keyword:
        return jsonify({"success": False, "error": "缺少 keyword"})
    results = search_appstore_keyword(keyword)
    return jsonify({"success": True, "keyword": keyword, "data": results})

@app.route("/api/aso/suggestions/<product_id>")
def api_aso_suggestions(product_id):
    if product_id not in PRODUCTS:
        return jsonify({"success": False, "error": "无效 product_id"})
    suggestions = get_keyword_suggestions(product_id)
    return jsonify({"success": True, "data": suggestions})

# ─── CRM API ──────────────────────────────────────────────
@app.route("/api/crm/contacts", methods=["GET"])
def api_contacts_list():
    product = request.args.get("product")
    tag = request.args.get("tag")
    return jsonify({"success": True, "data": get_contacts(product, tag)})

@app.route("/api/crm/contacts", methods=["POST"])
def api_contacts_add():
    body = request.json or {}
    contact = add_contact(
        phone=body.get("phone", ""),
        name=body.get("name", ""),
        product_interest=body.get("product_interest", ""),
        tags=body.get("tags", []),
    )
    return jsonify({"success": True, "data": contact})

@app.route("/api/crm/campaigns", methods=["GET"])
def api_campaigns_list():
    return jsonify({"success": True, "data": get_campaigns()})

@app.route("/api/crm/campaigns", methods=["POST"])
def api_campaigns_create():
    body = request.json or {}
    campaign = create_campaign(
        name=body.get("name", ""),
        product_id=body.get("product_id", ""),
        message_template=body.get("message_template", ""),
        target_tag=body.get("target_tag", ""),
        schedule_time=body.get("schedule_time"),
    )
    return jsonify({"success": True, "data": campaign})

@app.route("/api/crm/campaigns/<int:cid>/send", methods=["POST"])
def api_campaigns_send(cid):
    result = send_campaign(cid)
    return jsonify(result)

@app.route("/api/crm/campaigns/recall", methods=["POST"])
def api_recall():
    body = request.json or {}
    product_id = body.get("product_id", "")
    msg = body.get("message", "")
    campaign = create_recall_campaign(product_id, msg)
    return jsonify({"success": True, "data": campaign})

@app.route("/api/crm/logs")
def api_crm_logs():
    cid = request.args.get("campaign_id")
    logs = get_send_logs(int(cid) if cid else None)
    return jsonify({"success": True, "data": logs})

# ─── Dashboard API ────────────────────────────────────────
@app.route("/api/model-status")
def api_model_status():
    from copywriter import get_model_status
    return jsonify({"success": True, "data": get_model_status()})



    posts = get_all_posts()
    contacts = get_contacts()
    campaigns = get_campaigns()
    hotspots = _hotspot_cache.get("data") or {}
    return jsonify({
        "success": True,
        "data": {
            "total_posts": len(posts),
            "published_posts": len([p for p in posts if p["status"] == "published"]),
            "pending_posts": len([p for p in posts if p["status"] == "pending"]),
            "total_contacts": len(contacts),
            "total_campaigns": len(campaigns),
            "hotspot_count": hotspots.get("total", 0),
            "last_hotspot_update": hotspots.get("collected_at", "未采集"),
            "posts_by_platform": _count_by(posts, "platform_id"),
            "posts_by_product": _count_by(posts, "product_id"),
        }
    })


def _count_by(items, key):
    result = {}
    for item in items:
        k = item.get(key, "unknown")
        result[k] = result.get(k, 0) + 1
    return result


if __name__ == "__main__":
    from scheduler import start_scheduler
    start_scheduler()
    port = int(os.getenv("PORT", 5000))
    print(f"\n🚀 推广自动化系统已启动！")
    print(f"   访问地址: http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
