"""
即创平台工具函数 - 复用之前的代码逻辑
包含数字人口播按钮定位、智能形象匹配等通用功能
"""
import re


def click_digital_human_broadcast(page):
    """
    点击数字人口播按钮 - 复用之前的代码
    尝试多种定位方式确保成功
    """
    print("🎬 正在点击数字人口播按钮...")
    digital_human_found = False
    
    # 等待页面加载
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(5000)
    
    # 尝试点击第2个数字人口播元素（根据codegen生成的代码）
    try:
        digital_human_broadcast = page.get_by_text("数字人口播").nth(1)
        digital_human_broadcast.wait_for(state="visible", timeout=15000)
        digital_human_broadcast.click(force=True)
        print("✅ 已点击数字人口播（第2个元素）")
        page.wait_for_timeout(5000)
        digital_human_found = True
    except Exception as e:
        print(f"⚠️ 点击第2个数字人口播失败: {e}")
        # 尝试点击第1个数字人口播元素
        try:
            digital_human_broadcast = page.get_by_text("数字人口播").first
            digital_human_broadcast.wait_for(state="visible", timeout=15000)
            digital_human_broadcast.click(force=True)
            print("✅ 已点击数字人口播（第1个元素）")
            page.wait_for_timeout(5000)
            digital_human_found = True
        except Exception as e2:
            print(f"⚠️ 点击第1个数字人口播失败: {e2}")
            # 备选方案：使用更具体的选择器
            try:
                digital_human_broadcast = page.locator("div:has-text('数字人口播')").first
                digital_human_broadcast.wait_for(state="visible", timeout=15000)
                digital_human_broadcast.click(force=True)
                print("✅ 已点击数字人口播（卡片定位）")
                page.wait_for_timeout(5000)
                digital_human_found = True
            except Exception as e3:
                print(f"⚠️ 卡片定位数字人口播失败: {e3}")
                # 备选方案：使用按钮选择器
                try:
                    digital_human_broadcast = page.locator("button:has-text('数字人口播')").first
                    digital_human_broadcast.wait_for(state="visible", timeout=15000)
                    digital_human_broadcast.click(force=True)
                    print("✅ 已点击数字人口播（按钮定位）")
                    page.wait_for_timeout(5000)
                    digital_human_found = True
                except Exception as e4:
                    print(f"⚠️ 按钮定位数字人口播失败: {e4}")
    
    return digital_human_found


def click_image_button(page):
    """
    点击形象按钮 - 复用之前的代码
    """
    print("👤 正在点击形象按钮...")
    image_button_found = False
    
    try:
        # 使用精准定位器
        image_button = page.locator("div").filter(has_text=re.compile(r"^形象$"))
        image_button.wait_for(state="visible", timeout=15000)
        image_button.click(force=True)
        print("✅ 已点击形象按钮（精准定位）")
        page.wait_for_timeout(3000)
        image_button_found = True
    except Exception as e:
        print(f"⚠️ 精准定位形象按钮失败: {e}")
        # 备选方案：使用文本定位
        try:
            image_button = page.locator('text=形象').first
            image_button.wait_for(state="visible", timeout=15000)
            image_button.click(force=True)
            print("✅ 已点击形象按钮（文本定位）")
            page.wait_for_timeout(3000)
            image_button_found = True
        except Exception as e2:
            print(f"⚠️ 文本定位形象按钮失败: {e2}")
    
    return image_button_found


def analyze_content_and_select_avatar(content):
    """
    智能分析文案内容并选择合适的数字人形象
    复用之前的智能匹配逻辑
    """
    if not content:
        print("⚠️ 文案为空，使用默认形象")
        return 0
    
    content_lower = content.lower()
    
    # 定义形象选择逻辑
    is_tech_finance = any(keyword in content_lower for keyword in ['科技', '金融', '资产', '安全', '保险', '投资', '理财', '数字', '遗产'])
    is_lifestyle = any(keyword in content_lower for keyword in ['生活', '时尚', '美食', '旅游', '健康', '美妆', '购物', '娱乐'])
    is_education = any(keyword in content_lower for keyword in ['教育', '学习', '知识', '培训', '课程', '考试', '学校'])
    is_news = any(keyword in content_lower for keyword in ['新闻', '热点', '事件', '报道', '资讯', '消息'])
    is_business = any(keyword in content_lower for keyword in ['商务', '创业', '职场', '工作', '公司', '管理'])
    is_family = any(keyword in content_lower for keyword in ['家庭', '亲情', '孩子', '父母', '家人', '婚姻'])
    
    print(f"📊 文案分析结果: 科技金融={is_tech_finance}, 生活方式={is_lifestyle}, 教育={is_education}, 新闻={is_news}, 商务={is_business}, 家庭={is_family}")
    
    # 基于分析结果选择形象
    if is_tech_finance:
        print("🎯 选择专业商务形象")
        return 0
    elif is_lifestyle:
        print("🎯 选择时尚潮流形象")
        return 2
    elif is_education:
        print("🎯 选择知性教师形象")
        return 1
    elif is_news:
        print("🎯 选择稳重专业形象")
        return 3
    elif is_business:
        print("🎯 选择商务精英形象")
        return 0
    elif is_family:
        print("🎯 选择亲切温和形象")
        return 1
    else:
        print("🎯 选择默认形象")
        return 0


def select_avatar_by_index(page, avatar_index):
    """
    根据索引选择数字人形象并点击确定
    支持多种选择器以提高成功率
    """
    try:
        # 等待形象选择面板出现
        page.wait_for_timeout(3000)
        
        # 尝试多种选择器定位数字人形象
        avatar_selectors = [
            page.locator(".vue-recycle-scroller__item-view > .cssMedia > .group > .jc-robot > img"),
            page.locator(".jc-robot > img"),
            page.locator(".avatar-item img"),
            page.locator("img[alt*='avatar'], img[alt*='Avatar']"),
            page.locator(".character-item img"),
            page.locator(".recycle-scroller-item img"),
            page.locator("div[class*='robot'] img"),
            page.locator(".vue-recycle-scroller__item-view img")
        ]
        
        avatars = None
        avatars_count = 0
        
        for selector in avatar_selectors:
            try:
                avatars_count = selector.count()
                if avatars_count > 0:
                    avatars = selector
                    print(f"✅ 使用选择器找到 {avatars_count} 个数字人形象")
                    break
            except:
                continue
        
        if avatars and avatars_count > 0:
            # 选择合适的形象
            if avatars_count > avatar_index:
                digital_avatar = avatars.nth(avatar_index)
            else:
                digital_avatar = avatars.first
                avatar_index = 0
            
            digital_avatar.wait_for(state="visible", timeout=15000)
            digital_avatar.click(force=True)
            print(f"✅ 已选择第{avatar_index + 1}个数字人形象")
            
            page.wait_for_timeout(2000)
            
            # 点击确定按钮
            confirm_button = page.get_by_role("button", name="确定")
            confirm_button.wait_for(state="visible", timeout=15000)
            confirm_button.click(force=True)
            print("✅ 已点击确定按钮")
            page.wait_for_timeout(3000)
            return True
        else:
            print("⚠️ 未找到数字人形象，尝试直接点击第一个可见形象")
            try:
                # 尝试找到页面上第一个可见的形象图片
                first_img = page.locator("img").first
                first_img.wait_for(state="visible", timeout=10000)
                first_img.click(force=True)
                print("✅ 已点击第一个可见图片作为形象")
                
                page.wait_for_timeout(2000)
                
                # 点击确定按钮
                confirm_button = page.get_by_role("button", name="确定")
                confirm_button.wait_for(state="visible", timeout=15000)
                confirm_button.click(force=True)
                print("✅ 已点击确定按钮")
                page.wait_for_timeout(3000)
                return True
            except Exception as e3:
                print(f"⚠️ 选择形象失败: {e3}")
                # 关闭形象选择弹窗，继续流程
                try:
                    popup_mask = page.locator(".ovui-popup__mask")
                    popup_mask.click()
                    print("✅ 已关闭形象选择弹窗")
                except:
                    pass
                return False
    except Exception as e:
        print(f"⚠️ 选择数字人形象失败: {e}")
        return False


def handle_clipboard_permission(page):
    """
    处理剪贴板权限请求弹窗 - 自动点击允许
    根据截图使用更精确的定位方式
    """
    print("🔒 检查剪贴板权限弹窗...")
    
    # 尝试多种定位方式，按照优先级排列
    allow_button_locators = [
        # 方式1：直接通过文本定位允许按钮
        page.locator("button").filter(has_text="允许"),
        # 方式2：通过弹窗内容定位后找到按钮
        page.locator("div:has-text('查看复制到剪贴板的文字和图片')").locator("button").last,
        # 方式3：通过标题定位弹窗后找到按钮
        page.locator("div:has-text('aic.oceanengine.com 想要')").locator("button").last,
        # 方式4：使用 get_by_role
        page.get_by_role("button", name="允许"),
        # 方式5：使用 get_by_text
        page.get_by_text("允许"),
        # 方式6：使用属性选择器
        page.locator("button[aria-label='允许']"),
        # 方式7：使用 class 选择器
        page.locator(".btn-allow, .allow-btn"),
        # 方式8：使用相对定位
        page.locator("div").filter(has_text="屏蔽").locator("+ button"),
        # 方式9：通过弹窗容器定位
        page.locator("div[role='dialog'], div[role='alertdialog']").locator("button").last,
        # 方式10：直接选择页面上第二个按钮（屏蔽、允许）
        page.locator("button").nth(1)
    ]
    
    for idx, allow_button in enumerate(allow_button_locators):
        try:
            allow_button.wait_for(state="visible", timeout=3000)
            allow_button.click(force=True)
            print(f"✅ 已允许剪贴板权限（使用方式 {idx + 1}）")
            page.wait_for_timeout(1500)
            return True
        except Exception as e:
            print(f"   方式 {idx + 1} 失败: {str(e)[:50]}")
            continue
    
    print("⚠️ 未找到剪贴板权限弹窗或已处理")
    return False


def paste_content_to_input(page, content):
    """
    将文案粘贴到输入框 - 使用右键菜单粘贴，绕过剪贴板权限弹窗
    """
    print("📝 正在粘贴文案到输入框...")
    
    input_element = None
    
    input_locators = [
        page.locator("div[contenteditable='true']").first,
        page.locator("div.aic-prompt-input").first,
        page.locator("div.ProseMirror").first,
        page.locator(".text-sm.px-1\\.5 div").first,
        page.get_by_role("textbox").first,
    ]
    
    for idx, locator in enumerate(input_locators):
        try:
            locator.wait_for(state="visible", timeout=5000)
            input_element = locator
            print(f"✅ 找到文案输入框（方式 {idx + 1}）")
            break
        except Exception as e:
            print(f"   方式 {idx + 1} 失败: {str(e)[:30]}")
            continue
    
    if input_element:
        try:
            input_element.click(force=True)
            page.wait_for_timeout(1000)
            
            try:
                page.keyboard.press("Control+A")
                page.wait_for_timeout(300)
                page.keyboard.press("Delete")
                page.wait_for_timeout(300)
            except:
                pass
            
            print("� 尝试获取剪贴板内容并直接设置...")
            
            # 获取剪贴板内容
            clipboard_text = ""
            try:
                clipboard_text = page.evaluate("navigator.clipboard.readText()")
                print(f"✅ 成功读取剪贴板，内容长度: {len(clipboard_text)}")
            except Exception as e:
                print(f"⚠️ 读取剪贴板失败: {e}")
                if content:
                    clipboard_text = content
                    print(f"📝 使用传入的文案内容，长度: {len(content)}")
            
            if clipboard_text and clipboard_text.strip():
                # 使用JS直接设置输入框内容
                print("🔧 使用JS设置输入框内容...")
                result = page.evaluate("(text) => { const selectors = ['div[contenteditable=\"true\"]', 'div.aic-prompt-input', 'div.ProseMirror', '.text-sm div', '.px-1\\5c.5 div']; let element; for(let sel of selectors) { try { element = document.querySelector(sel); if(element) break; } catch(e) {} } if (element) { element.innerText = text; element.dispatchEvent(new Event('input', { bubbles: true })); element.dispatchEvent(new Event('change', { bubbles: true })); return true; } return false; }", clipboard_text[:2000])
                if result:
                    print(f"✅ 已设置文案内容，长度: {min(len(clipboard_text), 2000)}")
                else:
                    print("❌ JS设置内容失败")
                    return False
            else:
                print("❌ 没有可用的文案内容")
                return False
            
            try:
                result = page.evaluate("""
                    (function() {
                        const active = document.activeElement;
                        if (active && active.innerText) {
                            return {length: active.innerText.length, preview: active.innerText.substring(0, 50)};
                        }
                        return {length: 0, preview: ''};
                    })()
                """)
                if result['length'] > 0:
                    print(f"✅ 粘贴成功！内容长度: {result['length']} 字符")
                    print(f"   内容预览: {result['preview']}...")
                    return True
                else:
                    print("⚠️ 粘贴后内容为空")
                    if content:
                        print("🔧 尝试直接输入文案...")
                        input_element.click(force=True)
                        page.keyboard.type(content[:2000])
                        print(f"✅ 已直接输入文案，长度: {min(len(content), 2000)}")
                        return True
                    return False
            except Exception as e:
                print(f"⚠️ 验证粘贴内容失败: {e}")
                return True
            
        except Exception as e:
            print(f"⚠️ 粘贴文案时出错: {e}")
            return False
    else:
        print("❌ 未找到文案输入框")
        return False


def wait_for_script_analysis(page):
    """
    等待脚本解析完成（显示进度条时等待）
    """
    print("⏳ 等待脚本解析完成...")
    
    max_wait_time = 120000  # 最大等待2分钟
    start_time = page.evaluate("Date.now()")
    
    while True:
        current_time = page.evaluate("Date.now()")
        if current_time - start_time > max_wait_time:
            print("⚠️ 脚本解析超时")
            return False
            
        try:
            # 检查是否存在进度条或解析中的提示
            is_analyzing = False
            
            # 检查"脚本拆行解析中"提示
            try:
                if page.locator("text=脚本拆行解析中").count() > 0:
                    is_analyzing = True
            except:
                pass
            
            # 检查"脚本内容审核中"提示
            try:
                if page.locator("text=脚本内容审核中").count() > 0:
                    is_analyzing = True
            except:
                pass
            
            # 检查进度条
            try:
                if page.locator(".progress-bar").count() > 0:
                    is_analyzing = True
            except:
                pass
            
            # 检查loading状态
            try:
                if page.locator("[class*='loading'], [class*='loading']").count() > 0:
                    is_analyzing = True
            except:
                pass
            
            if not is_analyzing:
                print("✅ 脚本解析完成")
                break
            
            print("⏳ 脚本解析中...")
            page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"⚠️ 检查解析状态时出错: {e}")
            page.wait_for_timeout(3000)
    
    page.wait_for_timeout(2000)
    return True


def wait_for_video_generation(page):
    """
    等待视频生成完成（检测进度条到100%或超时自动继续）
    """
    print("⏳ 正在等待视频生成完成...")
    
    max_wait_time = 180000  # 最大等待3分钟（缩短超时时间）
    start_time = page.evaluate("Date.now()")
    last_progress = ""
    
    while True:
        current_time = page.evaluate("Date.now()")
        if current_time - start_time > max_wait_time:
            print("⚠️ 视频生成超时，继续处理下一个热点")
            return False
            
        try:
            # 检查是否显示"正在生成视频"的提示
            generation_in_progress = False
            
            # 检查进度百分比（包括99%以上视为完成）
            try:
                progress_text = page.locator("text=100%").first
                if progress_text.is_visible():
                    print("✅ 视频生成完成（进度100%）")
                    break
            except:
                pass
            
            # 检查进度百分比（99%也视为基本完成，继续下一个）
            try:
                progress_text = page.locator("text=99%").first
                if progress_text.is_visible():
                    print("⏳ 视频生成中... 99%")
                    generation_in_progress = True
            except:
                pass
            
            # 检查是否有进度条
            try:
                progress_elements = page.locator("div[role='progressbar'], .progress, [class*='progress']")
                if progress_elements.count() > 0:
                    generation_in_progress = True
            except:
                pass
            
            # 检查"正在生成视频"文字
            try:
                if page.locator("text=正在生成视频").count() > 0:
                    generation_in_progress = True
            except:
                pass
            
            # 检查分析画面提示
            try:
                if page.locator("text=正在分析视频画面").count() > 0:
                    generation_in_progress = True
            except:
                pass
            
            # 检查进度数字（如 "24%"）
            try:
                progress_nums = page.locator("text=%").all_text_contents()
                if progress_nums:
                    generation_in_progress = True
            except:
                pass
            
            if not generation_in_progress:
                # 检查"立即生成"按钮是否重新出现（表示上一个视频已完成）
                try:
                    generate_btn = page.get_by_role("button", name="立即生成")
                    if generate_btn.is_visible():
                        print("✅ 视频生成完成（立即生成按钮重新出现）")
                        break
                except:
                    pass
                
                # 如果没有任何生成中的提示，认为已完成
                print("✅ 视频生成完成")
                break
            
            # 获取当前进度
            try:
                progress_texts = page.locator("text=%").all_text_contents()
                if progress_texts:
                    print(f"⏳ 视频生成中... {progress_texts[-1] if progress_texts else ''}")
            except:
                print("⏳ 视频生成中...")
            
            page.wait_for_timeout(5000)  # 每5秒检查一次
            
        except Exception as e:
            print(f"⚠️ 检查视频生成状态时出错: {e}")
            page.wait_for_timeout(5000)
    
    # 额外等待保存按钮出现
    print("⏳ 等待保存按钮出现...")
    try:
        save_button = page.get_by_role("button", name="保存")
        save_button.wait_for(state="visible", timeout=30000)
        print("✅ 保存按钮已出现")
    except Exception as e:
        print(f"⚠️ 等待保存按钮超时，继续执行: {e}")
    
    page.wait_for_timeout(2000)
    return True


def click_generate_button(page):
    """
    点击立即生成按钮 - 复用之前的代码
    包括等待脚本解析和视频生成完成
    """
    print("▶️ 正在点击立即生成按钮...")
    
    # 等待脚本解析完成
    wait_for_script_analysis(page)
    
    # 先滚动到页面底部，确保按钮在视口内
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        print("🔄 已滚动到页面底部")
        page.wait_for_timeout(1000)
    except:
        pass
    
    try:
        # 方法1：使用get_by_role定位器
        generate_btn = page.get_by_role("button", name="立即生成")
        generate_btn.wait_for(state="visible", timeout=15000)
        generate_btn.scroll_into_view_if_needed()
        generate_btn.click(force=True)
        print("✅ 已点击立即生成按钮（get_by_role定位）")
        
        # 等待视频生成开始（检测进度页面出现）
        if wait_for_generation_start(page):
            # 等待视频生成完成
            wait_for_video_generation(page)
            return True
        else:
            print("⚠️ 视频生成未开始，尝试其他方式")
            
    except Exception as e:
        print(f"⚠️ get_by_role定位立即生成按钮失败: {e}")
    
    # 备选方案：使用文本定位
    try:
        generate_btn = page.locator('text=立即生成').first
        generate_btn.wait_for(state="visible", timeout=15000)
        generate_btn.scroll_into_view_if_needed()
        generate_btn.click(force=True)
        print("✅ 已点击立即生成按钮（文本定位）")
        
        # 等待视频生成开始
        if wait_for_generation_start(page):
            wait_for_video_generation(page)
            return True
            
    except Exception as e2:
        print(f"⚠️ 文本定位立即生成按钮失败: {e2}")
    
    # 备选方案：使用CSS选择器（紫色按钮）
    try:
        generate_btn = page.locator("button.bg-purple-500, button.bg-purple-600").first
        generate_btn.wait_for(state="visible", timeout=15000)
        generate_btn.scroll_into_view_if_needed()
        generate_btn.click(force=True)
        print("✅ 已点击立即生成按钮（紫色按钮选择器）")
        
        # 等待视频生成开始
        if wait_for_generation_start(page):
            wait_for_video_generation(page)
            return True
            
    except Exception as e3:
        print(f"⚠️ 紫色按钮选择器定位失败: {e3}")
    
    # 备选方案：使用包含立即生成的按钮选择器
    try:
        generate_btn = page.locator("button:has-text('立即生成')").first
        generate_btn.wait_for(state="visible", timeout=15000)
        generate_btn.scroll_into_view_if_needed()
        generate_btn.click(force=True)
        print("✅ 已点击立即生成按钮（选择器定位）")
        
        # 等待视频生成开始
        if wait_for_generation_start(page):
            wait_for_video_generation(page)
            return True
            
    except Exception as e4:
        print(f"⚠️ 选择器定位立即生成按钮失败: {e4}")
    
    # 终极方案：使用JS强制点击
    try:
        result = page.evaluate("""
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.textContent && btn.textContent.includes('立即生成')) {
                    btn.scrollIntoView();
                    btn.click();
                    return true;
                }
            }
            return false;
        """)
        if result:
            print("✅ 已通过JS点击立即生成按钮")
            # 等待视频生成开始
            if wait_for_generation_start(page):
                wait_for_video_generation(page)
                return True
    except Exception as e5:
        print(f"⚠️ JS点击立即生成按钮失败: {e5}")
    
    print("❌ 所有点击方式均失败")
    return False


def wait_for_generation_start(page):
    """
    等待视频生成开始（检测"正在生成视频"页面出现）
    """
    print("⏳ 等待视频生成页面出现...")
    try:
        # 等待"正在生成视频"文字出现
        page.locator("text=正在生成视频").wait_for(state="visible", timeout=30000)
        print("✅ 视频生成已开始")
        return True
    except Exception as e:
        print(f"⚠️ 视频生成页面未出现: {e}")
        return False


def auto_login_jichuang(page):
    """
    自动登录即创平台 - 复用之前的代码
    包括自动勾选协议和点击同意登录
    """
    print("🔐 正在尝试自动登录即创平台...")
    
    login_attempts = 0
    max_login_attempts = 3
    
    while "login" in page.url.lower() or "account" in page.url.lower():
        login_attempts += 1
        if login_attempts > max_login_attempts:
            print("❌ 登录失败，已尝试多次")
            return False
        
        try:
            # 等待页面加载完成
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(5000)
            
            # 方法1：尝试使用get_by_role定位器（推荐）
            checkbox_found = False
            try:
                print("✅ 尝试使用get_by_role定位器勾选协议...")
                checkbox = page.get_by_role("checkbox")
                checkbox.wait_for(state="visible", timeout=15000)
                checkbox.check(force=True)
                print("✅ 已勾选同意协议")
                page.wait_for_timeout(2000)
                checkbox_found = True
            except Exception as e:
                print(f"⚠️ get_by_role定位失败: {e}")
                
                # 方法2：尝试使用JS强制勾选（终极方案）
                print("✅ 尝试使用JS强制勾选协议...")
                try:
                    page.evaluate("""
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        if (checkboxes.length > 0) {
                            const cb = checkboxes[0];
                            cb.checked = true;
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    """)
                    print("✅ 已通过JS强制勾选协议")
                    page.wait_for_timeout(2000)
                    checkbox_found = True
                except Exception as e2:
                    print(f"⚠️ JS强制勾选失败: {e2}")
            
            # 点击同意登录按钮
            if checkbox_found:
                print("✅ 正在尝试点击同意登录按钮...")
                
                # 方法1：使用get_by_role定位器
                try:
                    login_button = page.get_by_role("button", name="同意登录")
                    login_button.wait_for(state="visible", timeout=15000)
                    login_button.click(force=True)
                    print("✅ 已点击同意登录")
                    page.wait_for_timeout(5000)
                except Exception as e:
                    print(f"⚠️ get_by_role定位登录按钮失败: {e}")
                    
                    # 方法2：使用文本定位
                    try:
                        login_button = page.locator('text=同意登录')
                        login_button.wait_for(state="visible", timeout=15000)
                        login_button.click(force=True)
                        print("✅ 已点击同意登录")
                        page.wait_for_timeout(5000)
                    except Exception as e2:
                        print(f"⚠️ 文本定位登录按钮失败: {e2}")
            
            # 等待页面跳转（登录完成后会跳转到工作台）
            print("⏳ 等待登录完成...")
            page.wait_for_url("**", timeout=300000)  # 5分钟超时
            print(f"✅ 登录成功，当前URL: {page.url}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ 自动登录失败: {e}")
    
    print("✅ 已经登录或无需登录")
    return True
