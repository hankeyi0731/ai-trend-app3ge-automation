#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化发布脚本
当用户打开 http://127.0.0.1:5001 时自动启动
逐个处理每个匹配度≥60的热点
"""
import sys
import time
import os
import json
from playwright.sync_api import sync_playwright

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

# Cookie保存和复用功能
COOKIES_DIR = os.path.join(os.path.dirname(__file__), "cookies")
os.makedirs(COOKIES_DIR, exist_ok=True)


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


def auto_publish_all_hotspots():
    """自动处理所有匹配度≥60的热点"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            # 创建浏览器上下文时预先授予剪贴板读取权限，避免权限弹窗
            context = browser.new_context(
                permissions=["clipboard-read", "clipboard-write"],
                # 设置时区和语言
                locale="zh-CN",
                timezone_id="Asia/Shanghai"
            )
            page = context.new_page()
            
            # 步骤1：打开首页并获取热点数据
            print("🚀 步骤1：打开首页并获取热点数据")
            page.goto("http://127.0.0.1:5001")
            page.wait_for_timeout(3000)
            
            # 等待热点列表加载
            page.wait_for_selector("table", timeout=30000)
            print("✅ 热点列表已加载")
            
            # 步骤2：逐个处理匹配度≥60的热点
            print("\n🔍 正在查找匹配度≥60的热点...")
            
            # 获取所有热点行
            hotspots = page.query_selector_all("tr")
            print(f"找到 {len(hotspots)} 个热点行")
            
            processed_count = 0
            jichuang_page = None  # 初始化即创页面变量，用于复用
            
            for i, hotspot_row in enumerate(hotspots):
                try:
                    # 检查匹配度
                    match_score = None
                    try:
                        # 查找匹配度元素
                        match_elements = hotspot_row.query_selector_all("div, span")
                        for elem in match_elements:
                            text = elem.text_content()
                            if text and text.isdigit() and 0 <= int(text) <= 100:
                                match_score = int(text)
                                break
                    except:
                        pass
                    
                    # 只处理匹配度≥60的热点
                    if not match_score or match_score < 60:
                        continue
                    
                    processed_count += 1
                    print(f"\n📌 正在处理第 {processed_count} 个热点（匹配度: {match_score}）")
                    
                    # 查找"生成文案"按钮
                    generate_btn = hotspot_row.query_selector("button:has-text('生成文案')")
                    if not generate_btn:
                        print("❌ 未找到生成文案按钮")
                        continue
                    
                    # 点击"生成文案"按钮
                    print("📝 点击生成文案按钮...")
                    generate_btn.click(force=True)
                    page.wait_for_timeout(3000)
                    
                    # 步骤3：在弹窗中生成文案
                    print("📝 步骤3：在弹窗中生成文案")
                    
                    # 等待弹窗出现
                    print("⏳ 正在等待弹窗出现...")
                    popup_found = False
                    
                    # 尝试多种弹窗定位方式
                    popup_locators = [
                        page.locator("#genModal"),  # 通过ID定位
                        page.locator("div:has-text('生成文案')"),  # 通过文本定位
                        page.locator("div[style*='display: flex']"),  # 通过样式定位
                        page.locator("div[style*='position: fixed']"),  # 通过固定定位定位
                        page.locator("div.modal"),  # 通过modal类定位
                        page.locator("div#genModal"),  # 完整ID定位
                        page.locator("div").filter(has_text="生成文案")  # 过滤器定位
                    ]
                    
                    for locator in popup_locators:
                        try:
                            locator.wait_for(state="visible", timeout=5000)
                            print("✅ 文案生成弹窗已出现")
                            popup_found = True
                            break
                        except:
                            continue
                    
                    if not popup_found:
                        print("❌ 未找到弹窗，尝试直接操作")
                        # 尝试直接操作元素
                        try:
                            # 直接查找平台选择器
                            platform_select = page.locator("#genPlatforms")
                            platform_select.wait_for(state="visible", timeout=5000)
                            print("✅ 直接找到平台选择器")
                            popup_found = True
                        except:
                            print("❌ 无法找到弹窗或平台选择器")
                            # 关闭可能存在的页面
                            try:
                                # 不关闭主页面，只关闭可能的新标签页
                                for p in context.pages:
                                    if p != page:
                                        p.close()
                                page.wait_for_timeout(2000)
                            except:
                                pass
                            continue
                    
                    # 查找最佳匹配产品并选择
                    print("🔄 正在选择目标产品...")
                    try:
                        # 先获取热点的最佳匹配产品信息
                        # 从热点行中提取产品信息
                        product_info = None
                        try:
                            product_elems = hotspot_row.query_selector_all("div, span")
                            for elem in product_elems:
                                text = elem.text_content()
                                if text and ("解铃" in text or "轻于鸿毛" in text or "猫上有钱" in text):
                                    product_info = text
                                    break
                        except:
                            pass
                        
                        # 选择对应的产品选项
                        if product_info:
                            print(f"🎯 选择产品: {product_info}")
                            # 查找产品单选按钮并点击
                            product_selector = page.locator(f"div:has-text('{product_info}')").first
                            product_selector.wait_for(state="visible", timeout=10000)
                            product_selector.click(force=True)
                            page.wait_for_timeout(1000)
                        else:
                            print("⚠️ 未找到产品信息，使用默认产品")
                            # 默认选择第一个产品
                            first_product = page.locator("label:has-text('解铃')").first
                            first_product.wait_for(state="visible", timeout=10000)
                            first_product.click(force=True)
                            page.wait_for_timeout(1000)
                    except Exception as e:
                        print(f"⚠️ 选择产品时出错: {e}")
                        # 尝试使用默认产品
                        try:
                            first_product = page.locator("label:has-text('解铃')").first
                            first_product.wait_for(state="visible", timeout=10000)
                            first_product.click(force=True)
                            page.wait_for_timeout(1000)
                        except:
                            pass
                    
                    # 选择"抖音"平台
                    print("📱 正在选择抖音平台...")
                    platform_selected = False
                    
                    # 尝试多种定位方式
                    platform_locators = [
                        page.locator("select#genPlatforms"),
                        page.locator("select[name*='platform']"),
                        page.locator("select"),
                        page.locator("div:has-text('生成平台')").locator("select"),
                        page.locator("div").filter(has_text="生成平台").locator("select")
                    ]
                    
                    for platform_select in platform_locators:
                        try:
                            platform_select.wait_for(state="visible", timeout=5000)
                            # 尝试通过值选择
                            try:
                                platform_select.select_option("douyin")
                                print("✅ 已通过值选择抖音平台")
                                platform_selected = True
                                break
                            except:
                                # 尝试通过文本选择
                                try:
                                    platform_select.select_option(label="抖音")
                                    print("✅ 已通过文本选择抖音平台")
                                    platform_selected = True
                                    break
                                except:
                                    # 尝试通过索引选择（假设抖音是第4个选项）
                                    try:
                                        platform_select.select_option(index=3)
                                        print("✅ 已通过索引选择抖音平台")
                                        platform_selected = True
                                        break
                                    except:
                                        continue
                        except:
                            continue
                    
                    if not platform_selected:
                        print("⚠️ 无法选择抖音平台，尝试手动点击")
                        # 尝试点击抖音选项
                        try:
                            douyin_option = page.locator("option:has-text('抖音')").first
                            douyin_option.wait_for(state="visible", timeout=5000)
                            douyin_option.click(force=True)
                            print("✅ 已手动点击选择抖音平台")
                            platform_selected = True
                        except Exception as e:
                            print(f"❌ 无法选择抖音平台: {e}")
                    
                    if platform_selected:
                        print("✅ 已选择抖音平台")
                        page.wait_for_timeout(1000)
                    else:
                        print("⚠️ 未选择平台，使用默认平台")
                    
                    # 点击"开始生成"或"重新生成"按钮
                    print("⚡ 正在点击生成按钮...")
                    generate_clicked = False
                    
                    # 尝试多种生成按钮定位方式（包括"开始生成"和"重新生成"）
                    generate_button_locators = [
                        page.get_by_text("开始生成（调用通义千问）").first,
                        page.get_by_text("开始生成").first,
                        page.locator("button:has-text('开始生成')").first,
                        page.get_by_text("重新生成").first,  # 处理循环时的重新生成按钮
                        page.locator("button:has-text('重新生成')").first,
                        page.get_by_role("button", name="开始生成").first,
                        page.get_by_role("button", name="重新生成").first
                    ]
                    
                    for generate_btn in generate_button_locators:
                        try:
                            generate_btn.wait_for(state="visible", timeout=5000)
                            generate_btn.click(force=True)
                            print("✅ 已点击生成按钮")
                            generate_clicked = True
                            break
                        except Exception as e:
                            continue
                    
                    if not generate_clicked:
                        print("❌ 无法点击生成按钮")
                        # 关闭弹窗，继续下一个热点
                        try:
                            close_btn = page.locator("button:has-text('×'), button:has-text('关闭')").first
                            close_btn.wait_for(state="visible", timeout=5000)
                            close_btn.click(force=True)
                            page.wait_for_timeout(2000)
                        except:
                            pass
                        continue
                    
                    # 等待文案生成完成
                    print("⏳ 正在等待文案生成完成...")
                    page.wait_for_timeout(8000)  # 等待8秒
                    
                    # 先检查是否存在"重新生成"按钮，如果有则点击重新生成
                    print("🔄 检查是否需要重新生成...")
                    try:
                        regenerate_btn = page.locator("button:has-text('重新生成')").first
                        regenerate_btn.wait_for(state="visible", timeout=3000)
                        print("🔄 检测到重新生成按钮，点击重新生成...")
                        regenerate_btn.click(force=True)
                        print("✅ 已点击重新生成")
                        page.wait_for_timeout(10000)  # 等待重新生成完成
                    except:
                        print("✅ 无需重新生成")
                    
                    # 点击"复制"按钮
                    print("📋 正在点击复制按钮...")
                    try:
                        copy_btn = page.locator("button:has-text('复制')").first
                        copy_btn.wait_for(state="visible", timeout=15000)
                        copy_btn.click(force=True)
                        print("✅ 已复制文案")
                        page.wait_for_timeout(2000)
                    except Exception as e:
                        print(f"⚠️ 点击复制按钮时出错: {e}")
                    
                    # 步骤4：打开即创平台并生成视频（首次打开，后续复用）
                    print("\n🎬 步骤4：打开即创平台并生成视频")
                    
                    if jichuang_page is None:
                        # 首次打开即创平台
                        print("🌐 正在打开即创平台...")
                        jichuang_page = context.new_page()
                        
                        # 加载已保存的Cookie
                        cookies = _load_cookies("jichuang")
                        if cookies:
                            print("✅ 已加载保存的Cookie")
                            jichuang_page.context.add_cookies(cookies)
                        
                        jichuang_page.goto("https://aic.oceanengine.com/workbench?bpId=1858825698495691&type=ai_inspiration")
                        jichuang_page.wait_for_timeout(5000)
                        
                        # 检查是否需要登录并自动处理
                        login_success = auto_login_jichuang(jichuang_page)
                        
                        if login_success:
                            # 保存Cookie
                            cookies = jichuang_page.context.cookies()
                            _save_cookies("jichuang", cookies)
                            print("✅ 已保存登录Cookie")
                        else:
                            print("⚠️ 登录未完成，继续尝试后续操作")
                    else:
                        # 复用已打开的即创页面，刷新页面
                        print("🔄 复用已打开的即创页面...")
                        jichuang_page.reload()
                        jichuang_page.wait_for_timeout(5000)
                    
                    # 步骤5：点击"数字人口播" - 复用工具函数
                    print("🎬 步骤5：点击数字人口播")
                    digital_human_found = click_digital_human_broadcast(jichuang_page)
                    
                    # 步骤6：点击"形象"按钮 - 复用工具函数
                    print("👤 步骤6：点击形象按钮")
                    image_button_found = click_image_button(jichuang_page) if digital_human_found else False
                    
                    # 步骤7：智能选择数字人形象（根据文案内容匹配）- 复用工具函数
                    print("🎭 步骤7：智能选择数字人形象")
                    if image_button_found:
                        try:
                            # 获取当前剪贴板中的文案内容
                            clipboard_content = jichuang_page.evaluate("navigator.clipboard.readText()")
                            print(f"📋 剪贴板内容: {clipboard_content[:100]}...")
                            
                            # 分析文案并选择合适的形象 - 复用工具函数
                            avatar_index = analyze_content_and_select_avatar(clipboard_content)
                            
                            # 选择形象并确认 - 复用工具函数
                            select_avatar_by_index(jichuang_page, avatar_index)
                        except Exception as e:
                            print(f"⚠️ 智能选择数字人形象失败: {e}")
                    else:
                        print("⚠️ 未找到形象按钮，跳过形象选择")
                    
                    # 步骤8：粘贴文案到输入框 - 复用工具函数
                    print("📝 步骤8：粘贴文案到输入框")
                    try:
                        # 获取剪贴板内容
                        clipboard_content = jichuang_page.evaluate("navigator.clipboard.readText()")
                        paste_content_to_input(jichuang_page, clipboard_content)
                        
                        # 等待脚本审核完成（粘贴后会显示"脚本内容审核中..."）
                        print("⏳ 等待脚本审核完成...")
                        max_wait_time = 60000  # 最大等待1分钟
                        start_time = jichuang_page.evaluate("Date.now()")
                        while True:
                            current_time = jichuang_page.evaluate("Date.now()")
                            if current_time - start_time > max_wait_time:
                                print("⚠️ 脚本审核超时")
                                break
                            
                            # 检查是否还在审核中
                            try:
                                audit_elements = jichuang_page.locator("text=脚本内容审核中").count()
                                if audit_elements == 0:
                                    print("✅ 脚本审核完成")
                                    break
                            except:
                                print("✅ 脚本审核完成")
                                break
                            
                            jichuang_page.wait_for_timeout(2000)
                            
                    except Exception as e:
                        print(f"⚠️ 粘贴文案时出错: {e}")
                    
                    # 步骤9：点击"立即生成"按钮 - 复用工具函数（包含脚本解析等待和视频生成等待）
                    print("▶️ 步骤9：点击立即生成按钮")
                    click_generate_button(jichuang_page)
                    print("✅ 视频生成完成")
                    
                    # 关闭文案生成弹窗，准备处理下一个热点
                    print("🔄 正在关闭弹窗，准备处理下一个热点...")
                    try:
                        close_btn = page.locator("button:has-text('×'), button:has-text('关闭')").first
                        close_btn.wait_for(state="visible", timeout=5000)
                        close_btn.click(force=True)
                        page.wait_for_timeout(2000)
                    except:
                        pass
                    
                    # 保持即创页面打开，用于下一个热点
                    print("🔄 即创页面保持打开，准备处理下一个热点...")
                    
                    print(f"✅ 第 {processed_count} 个热点处理完成！")
                    
                except Exception as e:
                    print(f"❌ 处理热点时出错: {e}")
                    # 尝试关闭所有弹窗
                    try:
                        # 关闭即创页面
                        for p in context.pages:
                            if "oceanengine" in p.url:
                                p.close()
                        # 关闭文案生成弹窗
                        try:
                            close_btn = page.locator("button:has-text('×'), button:has-text('关闭')").first
                            close_btn.wait_for(state="visible", timeout=3000)
                            close_btn.click(force=True)
                            page.wait_for_timeout(2000)
                        except:
                            pass
                        # 确保主页面没有被关闭
                        if not page.is_closed():
                            print("✅ 主页面保持打开状态")
                        else:
                            print("⚠️ 主页面已关闭，重新打开")
                            # 重新打开主页面
                            page = context.new_page()
                            page.goto("http://127.0.0.1:5001")
                            page.wait_for_timeout(3000)
                    except Exception as close_error:
                        print(f"⚠️ 关闭弹窗时出错: {close_error}")
                    continue
            
            print(f"\n🎉 所有热点处理完成！共处理 {processed_count} 个热点")
            browser.close()
            return {"success": True, "processed_count": processed_count}
            
    except Exception as e:
        print(f"❌ 自动化流程失败: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("🚀 启动完全自动化发布流程...")
    result = auto_publish_all_hotspots()
    if result["success"]:
        print(f"✅ 自动化流程成功完成！")
    else:
        print(f"❌ 自动化流程失败: {result.get('error', '未知错误')}")
    sys.exit(0 if result["success"] else 1)
