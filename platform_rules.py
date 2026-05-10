"""
多平台规则配置模块
为每个平台提供详细的规则配置，包括内容限制、发布要求等
"""

PLATFORM_RULES = {
    "xiaohongshu": {
        "name": "小红书",
        "content_rules": {
            "max_length": 1000,
            "min_length": 100,
            "prohibited_words": ["最低价", "最优惠", "独家", "国家级", "世界级"],
            "required_elements": ["个人体验", "真实感受", "emoji使用"],
            "forbidden_content": ["硬广", "虚假宣传", "引流信息"]
        },
        "format_rules": {
            "title_required": True,
            "title_max_length": 20,
            "tags_required": True,
            "tags_count": "5-8",
            "image_required": True,
            "image_count": "3-9"
        },
        "posting_rules": {
            "max_posts_per_day": 5,
            "time_slots": ["08:00-10:00", "12:00-14:00", "18:00-22:00"],
            "content_type": "种草笔记"
        }
    },
    "weibo": {
        "name": "微博",
        "content_rules": {
            "max_length": 2000,
            "min_length": 50,
            "prohibited_words": ["转发抽奖", "必须关注", "限时抢购"],
            "required_elements": ["话题标签", "吸引眼球的开头"],
            "forbidden_content": ["诱导分享", "虚假信息", "敏感内容"]
        },
        "format_rules": {
            "title_required": False,
            "tags_required": True,
            "tags_count": "2-5",
            "image_required": False,
            "image_count": "1-9"
        },
        "posting_rules": {
            "max_posts_per_day": 10,
            "time_slots": ["09:00-11:00", "15:00-17:00", "20:00-23:00"],
            "content_type": "短内容"
        }
    },
    "zhihu": {
        "name": "知乎",
        "content_rules": {
            "max_length": 5000,
            "min_length": 300,
            "prohibited_words": ["广告", "推销", "虚假数据"],
            "required_elements": ["专业分析", "逻辑清晰", "个人经验"],
            "forbidden_content": ["低质内容", "抄袭", "恶意攻击"]
        },
        "format_rules": {
            "title_required": True,
            "title_max_length": 50,
            "tags_required": True,
            "tags_count": "3-5",
            "image_required": False,
            "image_count": "1-6"
        },
        "posting_rules": {
            "max_posts_per_day": 3,
            "time_slots": ["10:00-12:00", "19:00-22:00"],
            "content_type": "专业回答"
        }
    },
    "douyin": {
        "name": "抖音",
        "content_rules": {
            "max_length": 500,
            "min_length": 50,
            "prohibited_words": ["秒杀", "福利", "免费送"],
            "required_elements": ["3秒hook", "口播感", "节奏快"],
            "forbidden_content": ["低俗", "不良引导", "虚假宣传"]
        },
        "format_rules": {
            "title_required": True,
            "title_max_length": 30,
            "tags_required": True,
            "tags_count": "3-6",
            "image_required": False,
            "video_required": True
        },
        "posting_rules": {
            "max_posts_per_day": 5,
            "time_slots": ["12:00-14:00", "18:00-22:00"],
            "content_type": "短视频"
        }
    },
    "wechat_mp": {
        "name": "微信公众号",
        "content_rules": {
            "max_length": 10000,
            "min_length": 800,
            "prohibited_words": ["点击量", "阅读量", "粉丝数"],
            "required_elements": ["深度分析", "故事性", "排版美观"],
            "forbidden_content": ["诱导分享", "标题党", "虚假信息"]
        },
        "format_rules": {
            "title_required": True,
            "title_max_length": 20,
            "tags_required": False,
            "image_required": True,
            "image_count": "3-10"
        },
        "posting_rules": {
            "max_posts_per_day": 2,
            "time_slots": ["07:00-09:00", "20:00-22:00"],
            "content_type": "长文"
        }
    },
    "jichuang": {
        "name": "即创平台",
        "content_rules": {
            "max_length": 1000,
            "min_length": 100,
            "prohibited_words": ["最低价", "最优惠", "独家", "国家级", "世界级"],
            "required_elements": ["口语化", "有画面感", "节奏明快"],
            "forbidden_content": ["硬广", "虚假宣传", "引流信息"]
        },
        "format_rules": {
            "title_required": True,
            "title_max_length": 30,
            "tags_required": False,
            "video_required": True
        },
        "posting_rules": {
            "max_posts_per_day": 10,
            "time_slots": ["09:00-11:00", "15:00-17:00", "19:00-22:00"],
            "content_type": "视频脚本"
        }
    }
}


def get_platform_rules(platform_id):
    """获取指定平台的规则配置"""
    return PLATFORM_RULES.get(platform_id, {})


def validate_content(platform_id, content):
    """验证内容是否符合平台规则"""
    rules = get_platform_rules(platform_id)
    if not rules:
        return {"valid": True, "message": "平台规则未配置"}
    
    content_rules = rules.get("content_rules", {})
    
    # 检查长度
    length = len(content)
    max_length = content_rules.get("max_length", 10000)
    min_length = content_rules.get("min_length", 0)
    if length > max_length:
        return {"valid": False, "message": f"内容长度超过限制（{max_length}字）"}
    if length < min_length:
        return {"valid": False, "message": f"内容长度不足（至少{min_length}字）"}
    
    # 检查禁用词
    prohibited_words = content_rules.get("prohibited_words", [])
    for word in prohibited_words:
        if word in content:
            return {"valid": False, "message": f"包含禁用词：{word}"}
    
    return {"valid": True, "message": "内容符合规则"}


def get_optimal_posting_time(platform_id):
    """获取平台最佳发布时间"""
    rules = get_platform_rules(platform_id)
    if not rules:
        return []
    return rules.get("posting_rules", {}).get("time_slots", [])
