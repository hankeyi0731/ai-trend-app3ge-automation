import time
import json
import os
import threading
from datetime import datetime, timedelta

from platform_rules import get_optimal_posting_time, validate_content

_schedule_lock = threading.Lock()
_scheduled_posts = []  # [{id, keyword, product_id, platform_id, content, scheduled_time, status}]
_post_id_counter = 1


def add_scheduled_post(keyword, product_id, platform_id, content, scheduled_time_str=None):
    global _post_id_counter
    with _schedule_lock:
        # 验证内容是否符合平台规则
        validation = validate_content(platform_id, content)
        if not validation["valid"]:
            return {"error": validation["message"]}
        
        # 如果没有指定时间，自动选择最佳发布时间
        if not scheduled_time_str:
            scheduled_time_str = _get_next_optimal_time(platform_id)
        
        # 检查排程冲突
        if _has_schedule_conflict(platform_id, scheduled_time_str):
            # 自动调整到下一个可用时间
            scheduled_time_str = _find_next_available_time(platform_id, scheduled_time_str)
        
        post = {
            "id": _post_id_counter,
            "keyword": keyword,
            "product_id": product_id,
            "platform_id": platform_id,
            "content": content,
            "scheduled_time": scheduled_time_str,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
        }
        _scheduled_posts.append(post)
        _post_id_counter += 1
        return post


def get_all_posts():
    with _schedule_lock:
        return list(_scheduled_posts)


def get_post_by_id(post_id):
    with _schedule_lock:
        for p in _scheduled_posts:
            if p["id"] == post_id:
                return p
    return None


def update_post_status(post_id, status):
    with _schedule_lock:
        for p in _scheduled_posts:
            if p["id"] == post_id:
                p["status"] = status
                p["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
    return False


def delete_post(post_id):
    global _scheduled_posts
    with _schedule_lock:
        _scheduled_posts = [p for p in _scheduled_posts if p["id"] != post_id]


def get_due_posts():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    due = []
    with _schedule_lock:
        for p in _scheduled_posts:
            if p["status"] == "pending" and p["scheduled_time"][:16] <= now:
                due.append(p)
    return due


def _get_next_optimal_time(platform_id):
    """获取下一个最佳发布时间"""
    optimal_slots = get_optimal_posting_time(platform_id)
    now = datetime.now()
    
    # 今天的最佳时间
    for slot in optimal_slots:
        start_time, end_time = slot.split("-")
        start_hour, start_minute = map(int, start_time.split(":"))
        slot_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        if slot_start > now:
            return slot_start.strftime("%Y-%m-%d %H:%M:%S")
    
    # 明天的最佳时间
    tomorrow = now + timedelta(days=1)
    start_time, end_time = optimal_slots[0].split("-")
    start_hour, start_minute = map(int, start_time.split(":"))
    slot_start = tomorrow.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    return slot_start.strftime("%Y-%m-%d %H:%M:%S")


def _has_schedule_conflict(platform_id, scheduled_time_str):
    """检查是否有排程冲突"""
    scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")
    conflict_window = timedelta(minutes=30)  # 30分钟内视为冲突
    
    with _schedule_lock:
        for post in _scheduled_posts:
            if post["platform_id"] == platform_id and post["status"] == "pending":
                post_time = datetime.strptime(post["scheduled_time"], "%Y-%m-%d %H:%M:%S")
                if abs((scheduled_time - post_time).total_seconds()) < conflict_window.total_seconds():
                    return True
    return False


def _find_next_available_time(platform_id, scheduled_time_str):
    """寻找下一个可用的发布时间"""
    scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S")
    increment = timedelta(minutes=30)
    
    for i in range(1, 24):  # 最多尝试24次
        next_time = scheduled_time + (increment * i)
        next_time_str = next_time.strftime("%Y-%m-%d %H:%M:%S")
        if not _has_schedule_conflict(platform_id, next_time_str):
            return next_time_str
    
    return scheduled_time_str


def get_posts_by_platform(platform_id):
    """获取指定平台的所有排程"""
    with _schedule_lock:
        return [p for p in _scheduled_posts if p["platform_id"] == platform_id]


def get_posts_by_status(status):
    """获取指定状态的所有排程"""
    with _schedule_lock:
        return [p for p in _scheduled_posts if p["status"] == status]


def batch_update_posts(post_ids, status):
    """批量更新排程状态"""
    updated = 0
    with _schedule_lock:
        for post_id in post_ids:
            for p in _scheduled_posts:
                if p["id"] == post_id:
                    p["status"] = status
                    p["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    updated += 1
                    break
    return updated


def scheduler_loop():
    from publisher import publish_post
    while True:
        due = get_due_posts()
        for post in due:
            update_post_status(post["id"], "publishing")
            result = publish_post(post)
            if result.get("success"):
                update_post_status(post["id"], "published")
            else:
                update_post_status(post["id"], "failed")
        time.sleep(60)


def start_scheduler():
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
