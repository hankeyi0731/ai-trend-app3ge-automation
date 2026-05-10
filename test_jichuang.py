#!/usr/bin/env python3
"""
测试即创平台自动化发布功能
"""
import requests
import json

def test_jichuang_publish():
    """测试即创平台发布"""
    print("测试即创平台发布功能...")
    
    # 测试文案
    test_content = "你是否经常感到压力大，睡眠质量差？试试解铃契App，它能帮助你缓解压力，改善睡眠质量。通过科学的冥想和放松训练，让你的身心得到真正的休息。现在下载解铃契，开始你的健康生活吧！"
    
    # 测试发布API
    url = "http://127.0.0.1:5001/api/publish"
    data = {
        "platform_id": "jichuang",
        "content": test_content,
        "title": "测试即创平台发布"
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        result = response.json()
        print(f"发布结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get("success"):
            print("✅ 即创平台发布测试成功")
        else:
            print(f"❌ 即创平台发布测试失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_login_status():
    """测试登录状态"""
    print("\n测试登录状态...")
    url = "http://127.0.0.1:5001/api/login-status"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        print(f"登录状态: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_platform_rules():
    """测试平台规则"""
    print("\n测试平台规则...")
    url = "http://127.0.0.1:5001/api/platform-rules/jichuang"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        print(f"即创平台规则: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_login_status()
    test_platform_rules()
    test_jichuang_publish()
