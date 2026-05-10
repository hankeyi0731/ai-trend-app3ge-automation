import os
import requests
from pathlib import Path

# 主动加载 .env 文件（兼容未安装 python-dotenv 的情况）
def _load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

_load_env()

from matcher import PRODUCTS

# 模型优先级：先用 qwen-plus-2025-07-28，额度不足自动降级到 qwen3.5-plus
MODEL_PRIMARY = "qwen-plus-2025-07-28"
MODEL_FALLBACK = "qwen3.5-plus"

# 记录当前模型状态（运行时状态，重启后重置）
_model_state = {"current": MODEL_PRIMARY, "fallback_reason": ""}

PLATFORM_PROMPTS = {
    "xiaohongshu": {
        "name": "小红书",
        "style": "种草笔记风格：口语化、有个人真实感受、适当用emoji、结尾带话题标签，字数500-800字，禁止硬广感",
        "format": "开头用吸引人的金句或疑问句，中间分享感受/故事，末尾推荐产品+标签",
    },
    "zhihu": {
        "name": "知乎",
        "style": "专业回答风格：有逻辑、有深度、像一个有经验的过来人在分享，字数800-1500字",
        "format": "以回答问题形式，先共情问题，再分析原因，最后给出解决方案并自然带出产品",
    },
    "weibo": {
        "name": "微博",
        "style": "简短有力：抓眼球、制造共鸣或好奇心、带话题标签，字数100-200字",
        "format": "前两句制造共鸣或冲击感，中间1-2句介绍，结尾话题标签",
    },
    "douyin": {
        "name": "抖音",
        "style": "短视频文案/脚本：前3秒有超强hook，口播感强，节奏快，字数200-400字",
        "format": "0-3秒hook句（制造好奇/共鸣）+问题放大+解决方案展示+结尾CTA",
    },
    "wechat_mp": {
        "name": "微信公众号",
        "style": "深度长文：有故事性、有温度、排版意识强、适合深度阅读，字数1500-2500字",
        "format": "标题（10字内吸引人）+故事开头+问题分析+产品解决方案+总结升华",
    },
    "jichuang": {
        "name": "即创平台",
        "style": "视频脚本风格：口语化、有画面感、节奏明快、适合口播，字数300-500字",
        "format": "开头吸引注意（1-2句）+问题描述（2-3句）+产品解决方案（3-4句）+结尾呼吁行动（1-2句）",
    },
}


def build_copywriting_prompt(hotspot_keyword, product_id, platform_id, hot_value=0):
    product = PRODUCTS[product_id]
    platform = PLATFORM_PROMPTS[platform_id]

    prompt = f"""你是一位资深新媒体运营专家，擅长结合热点为App产品创作高转化率且符合平台规则的推广文案。

【今日热点】
热点词：{hotspot_keyword}
热度值：{hot_value}

【产品信息】
产品名：{product["name"]}
核心价值：{product["core_value"]}
目标用户：{product["target"]}
核心功能：{', '.join(product["features"])}
用户痛点：{', '.join(product["pain_points"])}
定价：{product["price"]}
Slogan：{product["slogan"]}

【发布平台】
平台：{platform["name"]}
写作风格要求：{platform["style"]}
内容结构要求：{platform["format"]}

【平台规则要求】
1. 禁止虚假宣传：不得夸大产品功能、效果或使用范围
2. 禁止引人误解：不得使用夸张性表达、提高心理预期等方式
3. 禁止价格误导：不得通过较低价格吸引用户但实际购买有较多限制
4. 禁止内容创作低质：不得使用负向剧情营销、博眼球、低俗暗示等内容
5. 禁止画面美观度低：不得使用清晰度低、大篇幅文字、背景颜色单一等素材
6. 禁止引流行为：不得包含联系方式、引导下载、引导加群等内容
7. 禁止违规行业：不得涉及医疗、金融、赌博等禁止投放的行业
8. 禁止无授权内容：不得涉及无授权的第三方产品、品牌或人物

【任务】
请结合热点「{hotspot_keyword}」，为产品「{product["name"]}」创作一篇适合{platform["name"]}发布的推广文案。

要求：
1. 自然融入热点，不要生硬蹭热度
2. 聚焦用户痛点，产生情感共鸣
3. 产品介绍要软性植入，不要有硬广感
4. 严格符合{platform["name"]}的平台调性和内容规范
5. 严格遵守平台规则要求，避免所有违规内容
6. 如需标签，在末尾用 # 开头列出5-8个相关话题标签
7. 直接输出文案正文，不要输出分析过程

请开始创作："""
    return prompt


def _call_model(input_text, stream=False, tools=None):
    """
    调用 Dashscope API 获取模型响应，支持模型优先级切换。
    支持兼容模式和新版接口的响应结构。
    """
    # 从环境变量中获取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY 未定义，请检查环境变量配置。")

    # 设置 API URL（兼容模式）
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/responses"

    # 构造请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 模型优先级
    models = [MODEL_PRIMARY, MODEL_FALLBACK]

    for model in models:
        # 构造请求体
        payload = {
            "model": model,
            "input": input_text,
            "stream": stream
        }

        if tools:
            payload["tools"] = tools

        try:
            # 发送 POST 请求
            response = requests.post(base_url, headers=headers, json=payload)
            response.raise_for_status()

            # 解析响应
            data = response.json()
            print(f"[DEBUG] API 响应结构: {data}")  # 添加调试信息

            # 尝试多种可能的输出路径
            content = None
            if "output" in data and isinstance(data["output"], list) and len(data["output"]) > 0:
                output_item = data["output"][0]
                if "content" in output_item and isinstance(output_item["content"], list):
                    for item in output_item["content"]:
                        if "text" in item:
                            content = item["text"]
                            break
            elif "output" in data and "text" in data["output"]:
                content = data["output"]["text"]

            if content is None:
                raise ValueError("API 响应格式无效或缺少输出内容。")

            return content

        except requests.exceptions.RequestException as e:
            # 如果是主模型失败，尝试备用模型
            if model == MODEL_PRIMARY:
                _model_state["current"] = MODEL_FALLBACK
                _model_state["fallback_reason"] = str(e)
                print(f"[模型降级] {MODEL_PRIMARY} 不可用，切换到 {MODEL_FALLBACK}")
            else:
                raise RuntimeError(f"请求 Dashscope API 时发生错误: {e}")
        except ValueError as ve:
            # 如果是主模型失败，尝试备用模型
            if model == MODEL_PRIMARY:
                _model_state["current"] = MODEL_FALLBACK
                _model_state["fallback_reason"] = str(ve)
                print(f"[模型降级] {MODEL_PRIMARY} 不可用，切换到 {MODEL_FALLBACK}")
            else:
                raise RuntimeError(f"解析 Dashscope API 响应时发生错误: {ve}")
        except Exception as e:
            print(f"[未知错误] 解析响应失败: {e}")
            raise RuntimeError(f"解析 Dashscope API 响应时发生错误: {e}")


def generate_copy_dashscope(prompt: str) -> str:
    """
    双模型策略：
      1. 优先使用 qwen-plus-2025-07-28
      2. 若遇额度/不可用错误，自动降级为 qwen3.5-plus 并记录原因
    """
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        return "[错误] 未配置 DASHSCOPE_API_KEY，请在 .env 文件中设置"
    try:
        content = _call_model(prompt)
        return content
    except Exception as e:
        return f"[请求失败] {e}"


def get_model_status() -> dict:
    """返回当前模型状态，供前端展示"""
    return {
        "current_model": _model_state["current"],
        "is_fallback": _model_state["current"] == MODEL_FALLBACK,
        "fallback_reason": _model_state["fallback_reason"],
        "primary_model": MODEL_PRIMARY,
        "fallback_model": MODEL_FALLBACK,
    }


def generate_all_copies(hotspot_keyword, product_id, hot_value=0, platforms=None):
    if platforms is None:
        platforms = list(PLATFORM_PROMPTS.keys())
    results = {}
    for platform_id in platforms:
        if platform_id not in PLATFORM_PROMPTS:
            continue
        prompt = build_copywriting_prompt(hotspot_keyword, product_id, platform_id, hot_value)
        content = generate_copy_dashscope(prompt)
        results[platform_id] = {
            "platform_name": PLATFORM_PROMPTS[platform_id]["name"],
            "content": content,
        }
    return results


def generate_copies_for_best_match(hotspot_item, platforms=None):
    keyword = hotspot_item.get("keyword", "")
    product_id = hotspot_item.get("best_match_id", "jielingqi")
    hot_value = hotspot_item.get("hot_value", 0)
    copies = generate_all_copies(keyword, product_id, hot_value, platforms)
    return {
        "hotspot": keyword,
        "platform_source": hotspot_item.get("platform", ""),
        "product_id": product_id,
        "product_name": PRODUCTS[product_id]["name"],
        "match_score": hotspot_item.get("match_score", 0),
        "copies": copies,
    }
