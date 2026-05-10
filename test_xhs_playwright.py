from playwright.sync_api import sync_playwright
import json
import time
import re

def fetch_xiaohongshu_hot():
    results = []
    
    try:
        with sync_playwright() as p:
            # 使用非无头模式，方便查看登录过程
            browser = p.chromium.launch(
                headless=False,
                executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            )
            
            # 创建页面时设置用户代理
            page = browser.new_page(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            )
            
            # 访问小红书首页
            page.goto('https://www.xiaohongshu.com/', timeout=60000)
            
            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=30000)
            
            # 等待用户登录
            print("请在浏览器中登录小红书，登录后按Enter键继续...")
            input()
            
            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=30000)
            
            # 访问热榜页面
            page.goto('https://www.xiaohongshu.com/explore/hot', timeout=60000)
            
            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=30000)
            
            # 等待更多时间让数据加载
            time.sleep(5)
            
            # 保存页面截图用于调试
            page.screenshot(path='xiaohongshu_hot.png')
            
            # 打印页面标题
            print(f"Page title: {page.title()}")
            
            # 尝试提取热点数据
            # 查找可能的热点项目
            hot_items = []
            
            # 尝试不同的选择器
            selectors = [
                '.hot-rank-item',
                '.hot-item',
                '.rank-item',
                'li.hot',
                '[class*="rank"]',
                '.hot-list-item',
                '.hot-board-item'
            ]
            
            for selector in selectors:
                try:
                    items = page.locator(selector).all()
                    if items:
                        hot_items = items
                        print(f"Found {len(hot_items)} hot items with selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            # 提取热点数据
            for i, item in enumerate(hot_items[:20]):
                try:
                    text = item.inner_text()
                    if text and len(text) > 5:
                        # 尝试提取排名和关键词
                        rank_match = re.match(r'^(\d+)\s*(.*)$', text.strip())
                        if rank_match:
                            rank = rank_match.group(1)
                            keyword = rank_match.group(2)
                        else:
                            rank = str(i + 1)
                            keyword = text.strip()
                        
                        results.append({
                            "keyword": keyword,
                            "hot_value": "",
                            "platform": "xiaohongshu",
                            "rank": rank,
                            "time": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    print(f"Error extracting item {i}: {e}")
            
            # 尝试通过网络请求获取热点数据
            if not results:
                print("Trying to get hot data from network requests...")
                try:
                    # 监听网络请求
                    hot_data = []
                    
                    def handle_response(response):
                        nonlocal hot_data
                        if 'hot' in response.url and response.status == 200:
                            try:
                                data = response.json()
                                hot_data.append(data)
                                print(f"Found hot data in response: {response.url}")
                            except Exception as e:
                                pass
                    
                    page.on('response', handle_response)
                    
                    # 刷新页面
                    page.reload()
                    time.sleep(5)
                    
                    if hot_data:
                        print(f"Found {len(hot_data)} hot data responses")
                        # 尝试解析热点数据
                        for data in hot_data:
                            if isinstance(data, dict):
                                # 尝试不同的数据结构
                                if 'hotList' in data:
                                    for item in data['hotList'][:20]:
                                        if isinstance(item, dict):
                                            keyword = item.get('keyword', item.get('title', ''))
                                            if keyword:
                                                results.append({
                                                    "keyword": keyword,
                                                    "hot_value": item.get('hotValue', ''),
                                                    "platform": "xiaohongshu",
                                                    "rank": item.get('rank', str(len(results) + 1)),
                                                    "time": time.strftime("%Y-%m-%d %H:%M:%S")
                                                })
                                elif 'data' in data:
                                    if isinstance(data['data'], dict) and 'hotList' in data['data']:
                                        for item in data['data']['hotList'][:20]:
                                            if isinstance(item, dict):
                                                keyword = item.get('keyword', item.get('title', ''))
                                                if keyword:
                                                    results.append({
                                                        "keyword": keyword,
                                                        "hot_value": item.get('hotValue', ''),
                                                        "platform": "xiaohongshu",
                                                        "rank": item.get('rank', str(len(results) + 1)),
                                                        "time": time.strftime("%Y-%m-%d %H:%M:%S")
                                                    })
                except Exception as e:
                    print(f"Error getting hot data from network: {e}")
            
            # 尝试打印页面的所有网络请求
            print("\nAll network requests:")
            requests = page.evaluate('''
                () => {
                    const requests = [];
                    if (window.performance && window.performance.getEntriesByType) {
                        const entries = window.performance.getEntriesByType('resource');
                        entries.forEach(entry => {
                            if (entry.name.includes('hot')) {
                                requests.push(entry.name);
                            }
                        });
                    }
                    return requests;
                }
            ''')
            for req in requests:
                print(f"- {req}")
            
            browser.close()
            
    except Exception as e:
        print(f"爬取小红书热榜失败: {e}")
    
    return results

if __name__ == "__main__":
    hotspots = fetch_xiaohongshu_hot()
    print(f"\n小红书热点数量: {len(hotspots)}")
    for i, item in enumerate(hotspots):
        print(f"{i+1}. {item['keyword']}")
    print(json.dumps(hotspots, ensure_ascii=False, indent=2))