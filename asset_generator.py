"""
推广素材自动生成：二维码、视频脚本、海报文字排版
"""
import os
import io
import json
import base64
from datetime import datetime

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

PRODUCTS = {
    "jielingqi":       {"name": "解铃契",   "color": (255, 105, 180), "color2": (255, 182, 193)},
    "maoshangyouqian": {"name": "猫上有钱", "color": (255, 107, 157), "color2": (255, 160, 122)},
    "qingyuhongmao":   {"name": "轻于鸿毛", "color": (74, 144, 217),  "color2": (123, 104, 238)},
}


def generate_qrcode_base64(url: str, size: int = 200) -> str:
    """生成二维码并返回 base64 图片字符串"""
    if not PIL_AVAILABLE:
        return ""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def generate_poster_text(product_id: str, headline: str, subtext: str, hotspot: str = "") -> dict:
    """生成海报文字内容结构（前端渲染用）"""
    product = PRODUCTS.get(product_id, {})
    r, g, b = product.get("color", (74, 144, 217))
    r2, g2, b2 = product.get("color2", (123, 104, 238))
    return {
        "product_name": product.get("name", ""),
        "headline": headline,
        "subtext": subtext,
        "hotspot_badge": hotspot,
        "color_primary": f"rgb({r},{g},{b})",
        "color_secondary": f"rgb({r2},{g2},{b2})",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def generate_video_script(keyword: str, product_id: str, product_info: dict) -> dict:
    """生成短视频脚本结构（60秒抖音/快手）"""
    name = product_info.get("name", "")
    slogan = product_info.get("slogan", "")
    pain = product_info.get("pain_points", [""])[0]
    feature = product_info.get("features", [""])[0]
    return {
        "title": f"【{keyword}】{name}推广视频脚本",
        "total_duration": "60秒",
        "scenes": [
            {
                "time": "0-3秒",
                "label": "黄金Hook",
                "visual": f"特写画面：与「{keyword}」相关的场景",
                "voiceover": f"你有没有遇到过这种情况……【与{keyword}相关的痛点场景描述】",
                "text_overlay": f"❗ {pain}",
            },
            {
                "time": "3-15秒",
                "label": "痛点放大",
                "visual": "镜头拉远，展示问题全貌，表情特写",
                "voiceover": f"这个问题困扰了太多人，但大多数人都没找到真正有效的方法……",
                "text_overlay": "你是不是也这样？",
            },
            {
                "time": "15-40秒",
                "label": "解决方案",
                "visual": f"展示{name} App界面，流畅操作演示",
                "voiceover": f"直到我发现了{name}——{slogan}。{feature}，简单几步就能解决这个问题。",
                "text_overlay": f"✅ {name} · {slogan}",
            },
            {
                "time": "40-55秒",
                "label": "真实反馈",
                "visual": "用户评价截图或真实使用场景",
                "voiceover": f"用了之后我发现，原来这件事可以这么简单。",
                "text_overlay": "用户真实反馈 👇",
            },
            {
                "time": "55-60秒",
                "label": "行动号召",
                "visual": f"{name} App图标 + 下载引导",
                "voiceover": f"感兴趣的朋友，主页链接直接下载，新用户还有免费体验机会！",
                "text_overlay": f"📱 搜索「{name}」免费下载",
            },
        ],
        "bgm_suggestion": "轻快治愈类背景音乐，节奏稳定",
        "shooting_tips": [
            "竖屏拍摄 9:16 比例",
            "前3秒必须有强视觉冲击",
            "字幕全程显示，方便无声观看",
            "最后5秒固定展示产品名和下载引导",
        ],
    }


def generate_aso_keywords(product_id: str, product_info: dict) -> dict:
    """生成 ASO 关键词建议"""
    name = product_info.get("name", "")
    keywords = product_info.get("keywords", [])
    core = keywords[:5] if len(keywords) >= 5 else keywords
    long_tail = [f"{k}推荐" for k in keywords[5:10]] + [f"最好的{k}App" for k in keywords[:3]]
    competitor = ["心理咨询App", "情感陪伴", "宠物服务平台", "数字遗嘱"] if product_id == "jielingqi" else []
    return {
        "product": name,
        "core_keywords": core,
        "long_tail_keywords": long_tail[:8],
        "competitor_keywords": competitor,
        "title_suggestion": f"{name}-{product_info.get('slogan','')}"[:30],
        "subtitle_suggestion": product_info.get("core_value", "")[:30],
        "keyword_field": "，".join(core + long_tail[:3]),
    }
