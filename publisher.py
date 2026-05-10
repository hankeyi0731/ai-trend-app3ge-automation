"""
跨平台自动化发布模块 (Playwright)
每个平台的 publish_* 函数实现具体的浏览器自动化操作
首次使用需要手动登录一次保存 Cookie，之后自动复用
"""
import os
import json
import re
from datetime import datetime

COOKIES_DIR = os.path.join(os.path.dirname(__file__), "cookies")
os.makedirs(COOKIES_DIR, exist_ok=True)

# 导入即创平台工具函数
from jichuang_utils import (
    click_digital_human_broadcast,
    click_image_button,
    analyze_content_and_select_avatar,
    select_avatar_by_index,
    paste_content_to_input,
    click_generate_button,
    auto_login_jichuang
)


def _get_cookie_path(platform_id):
    return os.path.join(COOKIES_DIR, f"{platform_id}_cookies.json")


def _save_cookies(platform_id, cookies):
    path = _get_cookie_path(platform_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


def _load_cookies(platform_id):
    path = _get_cookie_path(platform_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _has_cookies(platform_id):
    return os.path.exists(_get_cookie_path(platform_id))


def publish_xiaohongshu(content, title="", images=None):
    """小红书自动发布（Playwright）"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            cookies = _load_cookies("xiaohongshu")
            if cookies:
                context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://creator.xiaohongshu.com/publish/publish")
            page.wait_for_timeout(3000)
            # 检查是否已登录
            if "login" in page.url.lower():
                return {"success": False, "error": "小红书未登录，请先运行 login_platforms.py 完成登录"}
            # 点击图文发布
            try:
                page.click("text=上传图片")
                page.wait_for_timeout(2000)
            except Exception:
                pass
            # 填写标题
            if title:
                title_input = page.query_selector("input[placeholder*='标题']")
                if title_input:
                    title_input.fill(title[:20])
            # 填写正文
            content_area = page.query_selector("div[contenteditable='true']")
            if content_area:
                content_area.click()
                page.keyboard.type(content[:900])
            page.wait_for_timeout(2000)
            # 保存 cookies
            _save_cookies("xiaohongshu", context.cookies())
            browser.close()
        return {"success": True, "platform": "小红书", "message": "发布成功"}
    except ImportError:
        return {"success": False, "error": "请先安装 playwright: pip install playwright && playwright install chromium"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def publish_weibo(content):
    """微博自动发布（Playwright）"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            cookies = _load_cookies("weibo")
            if cookies:
                context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://weibo.com")
            page.wait_for_timeout(3000)
            if "passport" in page.url:
                return {"success": False, "error": "微博未登录，请先运行 login_platforms.py"}
            textarea = page.query_selector("textarea.W_input")
            if not textarea:
                textarea = page.query_selector("[placeholder*='有什么新鲜事']")
            if textarea:
                textarea.click()
                page.keyboard.type(content[:2000])
                page.wait_for_timeout(1000)
                send_btn = page.query_selector("button.W_btn_a")
                if send_btn:
                    send_btn.click()
                    page.wait_for_timeout(2000)
            _save_cookies("weibo", context.cookies())
            browser.close()
        return {"success": True, "platform": "微博", "message": "发布成功"}
    except ImportError:
        return {"success": False, "error": "请先安装 playwright"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def publish_zhihu(content, title=""):
    """知乎自动发布想法（Playwright）"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            cookies = _load_cookies("zhihu")
            if cookies:
                context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://www.zhihu.com")
            page.wait_for_timeout(3000)
            if "login" in page.url:
                return {"success": False, "error": "知乎未登录"}
            # 点击写想法
            try:
                page.click("button[aria-label*='写想法'], button:has-text('写想法')")
                page.wait_for_timeout(2000)
                editor = page.query_selector("div.PublishXiangfa-editor div[contenteditable]")
                if editor:
                    editor.click()
                    page.keyboard.type(content[:2000])
                    page.wait_for_timeout(1000)
                    page.click("button:has-text('发布')")
                    page.wait_for_timeout(2000)
            except Exception as e:
                return {"success": False, "error": f"知乎操作失败: {e}"}
            _save_cookies("zhihu", context.cookies())
            browser.close()
        return {"success": True, "platform": "知乎", "message": "发布成功"}
    except ImportError:
        return {"success": False, "error": "请先安装 playwright"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def publish_bilibili(content, title=""):
    """B站动态自动发布（Playwright）"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            cookies = _load_cookies("bilibili")
            if cookies:
                context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://t.bilibili.com")
            page.wait_for_timeout(3000)
            editor = page.query_selector("div.bili-dyn-publishing__input div[contenteditable]")
            if editor:
                editor.click()
                page.keyboard.type(content[:2000])
                page.wait_for_timeout(1000)
                page.click("button.bili-dyn-publishing__action.launcher")
                page.wait_for_timeout(2000)
            _save_cookies("bilibili", context.cookies())
            browser.close()
        return {"success": True, "platform": "B站", "message": "发布成功"}
    except ImportError:
        return {"success": False, "error": "请先安装 playwright"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def publish_jichuang(content="", title="", keyword=""):
    """即创平台自动发布（Playwright）- 完全自动化流程"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            
            # 步骤1：打开本地网站生成文案
            print("步骤1：正在打开本地网站生成文案...")
            page = context.new_page()
            page.goto("http://127.0.0.1:5001")
            page.wait_for_timeout(3000)
            
            # 点击生成文案按钮
            print("正在点击生成文案按钮...")
            try:
                generate_button = page.get_by_role("button", name="✍️ 生成文案").first
                generate_button.wait_for(state="visible", timeout=15000)
                generate_button.click(force=True)
                print("已点击生成文案按钮")
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"点击生成文案按钮失败: {e}")
                return {"success": False, "error": "点击生成文案按钮失败"}
            
            # 输入热点关键词
            if keyword:
                print(f"正在输入热点关键词: {keyword}")
                try:
                    keyword_input = page.locator("input[placeholder*='关键词']").first
                    keyword_input.wait_for(state="visible", timeout=15000)
                    keyword_input.click()
                    keyword_input.fill(keyword)
                    print(f"已输入关键词: {keyword}")
                    page.wait_for_timeout(1000)
                except Exception as e:
                    print(f"输入关键词失败: {e}")
            
            # 选择抖音平台
            print("正在选择抖音平台...")
            try:
                platform_select = page.locator("#genPlatforms")
                platform_select.wait_for(state="visible", timeout=15000)
                platform_select.select_option("douyin")
                print("已选择抖音平台")
                page.wait_for_timeout(1000)
            except Exception as e:
                print(f"选择抖音平台失败: {e}")
                return {"success": False, "error": "选择抖音平台失败"}
            
            # 点击开始生成按钮
            print("正在点击开始生成按钮...")
            try:
                start_button = page.get_by_role("button", name="⚡ 开始生成（调用通义千问）")
                start_button.wait_for(state="visible", timeout=15000)
                start_button.click(force=True)
                print("已点击开始生成按钮")
                page.wait_for_timeout(8000)  # 等待文案生成（增加等待时间）
            except Exception as e:
                print(f"点击开始生成按钮失败: {e}")
                return {"success": False, "error": "点击开始生成按钮失败"}
            
            # 复制生成的文案
            print("正在复制生成的文案...")
            try:
                copy_button = page.get_by_role("button", name="📋 复制").first
                copy_button.wait_for(state="visible", timeout=15000)
                copy_button.click(force=True)
                print("已复制生成的文案")
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"复制文案失败: {e}")
                return {"success": False, "error": "复制文案失败"}
            
            # 步骤2：打开即创平台
            print("步骤2：正在打开即创平台...")
            cookies = _load_cookies("jichuang")
            if cookies:
                context.add_cookies(cookies)
            page.goto("https://aic.oceanengine.com/workbench?bpId=1858825698495691&type=ai_inspiration")
            page.wait_for_timeout(5000)
            
            # 检查是否已登录并自动处理 - 复用工具函数
            auto_login_jichuang(page)
            
            # 导航到数字人口播页面 - 复用工具函数
            try:
                print("正在导航到数字人口播页面...")
                
                # 步骤1：点击"数字人口播" - 复用工具函数
                digital_human_found = click_digital_human_broadcast(page)
                
                # 步骤2：点击"形象"按钮 - 复用工具函数
                image_button_found = click_image_button(page) if digital_human_found else False
                
                # 步骤3：智能选择数字人形象（根据文案内容匹配）- 复用工具函数
                if image_button_found:
                    print("步骤3：正在根据文案内容智能选择数字人形象...")
                    try:
                        # 获取剪贴板内容
                        clipboard_content = page.evaluate("navigator.clipboard.readText()")
                        print(f"📋 剪贴板内容: {clipboard_content[:100]}...")
                        
                        # 分析文案并选择合适的形象 - 复用工具函数
                        avatar_index = analyze_content_and_select_avatar(clipboard_content)
                        
                        # 选择形象并确认 - 复用工具函数
                        select_avatar_by_index(page, avatar_index)
                    except Exception as e:
                        print(f"⚠️ 智能选择数字人形象失败: {e}")
                
                # 步骤4：将文案粘贴到输入框 - 复用工具函数
                print("步骤4：正在将文案粘贴到输入框...")
                try:
                    clipboard_content = page.evaluate("navigator.clipboard.readText()")
                    paste_content_to_input(page, clipboard_content)
                except Exception as e:
                    print(f"⚠️ 粘贴文案失败: {e}")
                
                # 步骤5：点击"立即生成"按钮 - 复用工具函数
                print("步骤5：正在点击立即生成按钮...")
                click_generate_button(page)
                
                # 等待视频生成
                print("正在等待视频生成，请耐心等待（可能需要30秒以上）...")
                page.wait_for_timeout(60000)  # 等待60秒让视频生成
                
                # 检查生成是否成功
                try:
                    success_elements = page.query_selector_all(
                        "div:has-text('生成成功'), div:has-text('Success'), div:has-text('Generated'), div:has-text('已完成')"
                    )
                    
                    if success_elements:
                        print("✓ 即创平台数字人口播视频生成成功！")
                    else:
                        print("即创平台数字人口播视频生成可能完成，请检查页面")
                except Exception as e:
                    print(f"检查生成状态时出错: {e}")
                    
            except Exception as e:
                print(f"即创平台操作失败: {e}")
            
            # 保存 cookies
            _save_cookies("jichuang", context.cookies())
            browser.close()
        return {"success": True, "platform": "即创平台", "message": "数字人口播视频生成成功"}
    except ImportError:
        return {"success": False, "error": "请先安装 playwright: pip install playwright && playwright install chromium"}
    except Exception as e:
        return {"success": False, "error": str(e)}


PLATFORM_PUBLISHERS = {
    "xiaohongshu": publish_xiaohongshu,
    "weibo": publish_weibo,
    "zhihu": publish_zhihu,
    "bilibili": publish_bilibili,
    "jichuang": publish_jichuang,
}


def publish_post(post: dict) -> dict:
    platform_id = post.get("platform_id", "")
    content = post.get("content", "")
    if platform_id not in PLATFORM_PUBLISHERS:
        return {"success": False, "error": f"暂不支持平台: {platform_id}"}
    publisher = PLATFORM_PUBLISHERS[platform_id]
    result = publisher(content)
    result["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result


def get_login_status():
    status = {}
    for pid in ["xiaohongshu", "weibo", "zhihu", "bilibili", "douyin", "jichuang"]:
        status[pid] = _has_cookies(pid)
    return status


def batch_publish_jichuang():
    """智能批量发布到即创平台
    自动筛选匹配度≥60的热点，根据最佳匹配产品选择目标产品，只勾选即创平台"""
    try:
        import requests
        
        # 获取热点数据
        print("正在获取热点数据...")
        response = requests.get("http://127.0.0.1:5001/api/hotspots")
        if response.status_code != 200:
            return {"success": False, "error": "获取热点数据失败"}
        
        hotspots = response.json().get("items", [])
        print(f"获取到 {len(hotspots)} 个热点")
        
        # 筛选匹配度≥60的热点
        filtered_hotspots = [h for h in hotspots if h.get("match_score", 0) >= 60]
        print(f"筛选出 {len(filtered_hotspots)} 个匹配度≥60的热点")
        
        if not filtered_hotspots:
            return {"success": False, "error": "没有匹配度≥60的热点"}
        
        # 依次处理每个热点
        results = []
        for i, hotspot in enumerate(filtered_hotspots, 1):
            keyword = hotspot.get("keyword", "")
            best_match_product = hotspot.get("best_match_product", "")
            best_match_id = hotspot.get("best_match_id", "")
            match_score = hotspot.get("match_score", 0)
            
            print(f"\n=== 处理第 {i}/{len(filtered_hotspots)} 个热点 ===")
            print(f"关键词: {keyword}")
            print(f"最佳匹配产品: {best_match_product}")
            print(f"匹配度: {match_score}")
            
            # 发布到即创平台
            result = publish_jichuang(keyword=keyword)
            results.append({
                "keyword": keyword,
                "product": best_match_product,
                "score": match_score,
                "result": result
            })
            
            # 等待一段时间，避免频繁操作
            print("等待3秒后处理下一个热点...")
            import time
            time.sleep(3)
        
        return {"success": True, "results": results, "total": len(results)}
    except Exception as e:
        return {"success": False, "error": str(e)}
