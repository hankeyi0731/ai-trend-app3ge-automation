"""
用户运营自动化：短信/邮件营销（复用阿里云短信服务）
"""
import os
import json
import time
import requests
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime, timedelta

ALIBABA_ACCESS_KEY_ID = os.getenv("ALIBABA_ACCESS_KEY_ID", "")
ALIBABA_ACCESS_KEY_SECRET = os.getenv("ALIBABA_ACCESS_KEY_SECRET", "")
SMS_SIGN_NAME = os.getenv("SMS_SIGN_NAME", "")

_contacts = []
_campaigns = []
_send_logs = []
_contact_id_counter = 1
_campaign_id_counter = 1


def add_contact(phone: str, name: str = "", product_interest: str = "", tags: list = None):
    global _contact_id_counter
    contact = {
        "id": _contact_id_counter,
        "phone": phone,
        "name": name,
        "product_interest": product_interest,
        "tags": tags or [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active",
    }
    _contacts.append(contact)
    _contact_id_counter += 1
    return contact


def get_contacts(product_filter: str = None, tag_filter: str = None) -> list:
    result = [c for c in _contacts if c["status"] == "active"]
    if product_filter:
        result = [c for c in result if c["product_interest"] == product_filter]
    if tag_filter:
        result = [c for c in result if tag_filter in c.get("tags", [])]
    return result


def create_campaign(name: str, product_id: str, message_template: str, target_tag: str = "", schedule_time: str = None):
    global _campaign_id_counter
    campaign = {
        "id": _campaign_id_counter,
        "name": name,
        "product_id": product_id,
        "message_template": message_template,
        "target_tag": target_tag,
        "schedule_time": schedule_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sent_count": 0,
        "success_count": 0,
    }
    _campaigns.append(campaign)
    _campaign_id_counter += 1
    return campaign


def get_campaigns() -> list:
    return list(_campaigns)


def _send_sms_aliyun(phone: str, template_code: str, params: dict) -> dict:
    """调用阿里云短信服务发送短信"""
    if not ALIBABA_ACCESS_KEY_ID or not ALIBABA_ACCESS_KEY_SECRET:
        return {"success": False, "error": "未配置阿里云AccessKey"}
    try:
        import datetime as dt
        timestamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        nonce = str(int(time.time() * 1000))
        query = {
            "AccessKeyId": ALIBABA_ACCESS_KEY_ID,
            "Action": "SendSms",
            "Format": "JSON",
            "PhoneNumbers": phone,
            "RegionId": "cn-hangzhou",
            "SignName": SMS_SIGN_NAME,
            "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": nonce,
            "SignatureVersion": "1.0",
            "TemplateCode": template_code,
            "TemplateParam": json.dumps(params, ensure_ascii=False),
            "Timestamp": timestamp,
            "Version": "2017-05-25",
        }
        sorted_query = sorted(query.items())
        encoded = "&".join(f"{urllib.parse.quote(k, safe='~')}={urllib.parse.quote(str(v), safe='~')}" for k, v in sorted_query)
        string_to_sign = f"GET&{urllib.parse.quote('/', safe='~')}&{urllib.parse.quote(encoded, safe='~')}"
        signing_key = ALIBABA_ACCESS_KEY_SECRET + "&"
        sig = base64.b64encode(hmac.new(signing_key.encode(), string_to_sign.encode(), hashlib.sha1).digest()).decode()
        query["Signature"] = sig
        url = "https://dysmsapi.aliyuncs.com/?" + "&".join(f"{k}={urllib.parse.quote(str(v), safe='~')}" for k, v in query.items())
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("Code") == "OK":
            return {"success": True, "request_id": data.get("RequestId")}
        return {"success": False, "error": data.get("Message", "未知错误")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_campaign(campaign_id: int) -> dict:
    campaign = next((c for c in _campaigns if c["id"] == campaign_id), None)
    if not campaign:
        return {"success": False, "error": "活动不存在"}
    contacts = get_contacts(
        product_filter=campaign["product_id"],
        tag_filter=campaign["target_tag"] or None,
    )
    if not contacts:
        return {"success": False, "error": "没有符合条件的用户"}
    campaign["status"] = "sending"
    sent, success = 0, 0
    for contact in contacts:
        msg = campaign["message_template"].replace("{name}", contact.get("name", "用户"))
        log = {
            "campaign_id": campaign_id,
            "phone": contact["phone"],
            "message": msg,
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        result = _send_sms_aliyun(contact["phone"], "SMS_TEMPLATE_CODE", {"content": msg[:70]})
        log["result"] = result
        _send_logs.append(log)
        sent += 1
        if result.get("success"):
            success += 1
        time.sleep(0.1)
    campaign["sent_count"] = sent
    campaign["success_count"] = success
    campaign["status"] = "completed"
    campaign["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"success": True, "sent": sent, "success_count": success}


def get_send_logs(campaign_id: int = None) -> list:
    if campaign_id:
        return [l for l in _send_logs if l["campaign_id"] == campaign_id]
    return list(_send_logs)


RECALL_TEMPLATES = {
    "jielingqi": "【解铃契】{name}，您还记得上次聊到孩子的问题吗？我们为您保留了记录，点击继续：",
    "maoshangyouqian": "【猫上有钱】{name}，附近有新的宠物可以预约撸哦～快来看看：",
    "qingyuhongmao": "【轻于鸿毛】{name}，您已超过7天未打卡，记得及时更新状态，保护重要信息安全。",
}


def create_recall_campaign(product_id: str, custom_msg: str = "") -> dict:
    template = custom_msg or RECALL_TEMPLATES.get(product_id, "")
    name = f"{product_id}_召回_{datetime.now().strftime('%m%d%H%M')}"
    return create_campaign(name=name, product_id=product_id, message_template=template, target_tag="inactive")
