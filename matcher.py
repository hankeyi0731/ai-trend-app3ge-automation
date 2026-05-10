import re

PRODUCTS = {
    "jielingqi": {
        "name": "解铃契",
        "slogan": "AI心理陪伴，记录成长轨迹",
        "core_value": "帮助家长解决孩子少儿情感及青春期问题，AI对话、问题卡片、时间轴记录孩子成长",
        "target": "有孩子的家长，孩子处于少儿情感期或青春期",
        "target_audience": "12-18岁青少年家长、教育工作者",
        "pain_points": ["孩子叛逆不沟通", "育儿焦虑", "不知道如何帮孩子疏导情绪", "孩子厌学", "亲子关系紧张"],
        "features": ["AI智能对话", "问题卡片自动生成", "成长时间轴", "情绪标签管理"],
        "price": "29元/月50次，超出1元/次，新用户1次免费",
        "color_primary": "#FF69B4",
        "color_secondary": "#FFB6C1",
        "keywords": ["青少年心理","亲子关系","育儿焦虑","叛逆期","情绪管理","厌学","孩子","青春期",
                     "家长","心理健康","沟通","教育","高考","中考","成长","校园","学习压力",
                     "作业","拖延","抑郁","焦虑","心理咨询","少儿","儿童","妈妈","爸爸"],
    },
    "maoshangyouqian": {
        "name": "猫上有钱",
        "slogan": "让撸宠更简单，让宠物更赚钱",
        "core_value": "连接撸宠人与铲屎官，宠物服务精准匹配，满足撸宠需求同时助力铲屎官获取收益",
        "target": "喜爱宠物但未养宠的撸宠人和有宠物愿意提供服务赚钱的铲屎官",
        "target_audience": "宠物爱好者、18-35岁年轻人",
        "pain_points": ["想撸猫但没有宠物","铲屎官宠物没有发挥价值","找不到靠谱宠物体验服务"],
        "features": ["双端平台（撸宠人/铲屎官）","地区精准匹配","宠物预约","需求发布","报价系统","订单管理"],
        "price": "平台撮合收益模式",
        "color_primary": "#FF6B9D",
        "color_secondary": "#FFA07A",
        "keywords": ["猫","狗","宠物","撸猫","撸狗","铲屎官","萌宠","宠物服务","宠物咖啡",
                     "猫咪","狗狗","宠物经济","宠物寄养","宠物美容","养宠","养猫","养狗",
                     "流浪猫","猫粮","宠物社交","撸猫馆","毛孩子","猫奴","狗奴"],
    },
    "qingyuhongmao": {
        "name": "轻于鸿毛",
        "slogan": "归期资留迹，莫教家人觅",
        "core_value": "数字遗产守护，用户打卡确认状态，停止打卡后自动将银行卡遗嘱等重要信息发给指定收件人",
        "target": "25-55岁关注资产安全有家庭责任感的成年人",
        "target_audience": "25-55岁有家庭有资产的成年人",
        "pain_points": ["意外后家人无法获取账户信息","数字资产无法传承","密码无人知晓","遗嘱无法及时送达"],
        "features": ["重要信息加密存储（银行卡/遗嘱）","打卡确认状态","30天未打卡自动发送","指定收件人管理","付费订阅"],
        "price": "月度5元/季度/年度50元订阅",
        "color_primary": "#4A90D9",
        "color_secondary": "#7B68EE",
        "keywords": ["遗嘱","遗产","数字遗产","资产传承","保险","意外","猝死","银行卡",
                     "密码","家人","数字资产","财产","生命","安全","资产保护",
                     "身后事","家庭资产","紧急联系人","财富传承","不测风云","万一"],
    },
}


def compute_match_score(keyword, product_id):
    product = PRODUCTS[product_id]
    score = 0.0
    for pk in product["keywords"]:
        if pk in keyword or keyword in pk:
            score += 40
            break
    for pain in product["pain_points"]:
        if any(w in keyword for w in pain[:4]):
            score += 20
            break
    for w in product["target"].replace("，", " ").split():
        if len(w) >= 2 and w in keyword:
            score += 15
            break
    for w in re.split(r"[，、。, ]", product["core_value"]):
        if len(w) >= 2 and w in keyword:
            score += 15
            break
    return min(score, 100.0)


def match_hotspot_to_products(keyword):
    results = []
    for pid, product in PRODUCTS.items():
        score = compute_match_score(keyword, pid)
        results.append({
            "product_id": pid,
            "product_name": product["name"],
            "score": score,
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def analyze_hotspots(hotspot_items):
    analyzed = []
    for item in hotspot_items:
        kw = item.get("keyword", "")
        matches = match_hotspot_to_products(kw)
        best = matches[0]
        analyzed.append({
            **item,
            "best_match_product": best["product_name"],
            "best_match_id": best["product_id"],
            "match_score": best["score"],
            "all_scores": {m["product_name"]: m["score"] for m in matches},
        })
    analyzed.sort(key=lambda x: x["match_score"], reverse=True)
    return analyzed
