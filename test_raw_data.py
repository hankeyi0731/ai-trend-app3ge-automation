import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler import fetch_all_hotspots

# 测试fetch_all_hotspots函数
result = fetch_all_hotspots()
print('Total items:', result.get('total', 0))

# 统计各平台的数量
platforms = {}
items = result.get('items', [])
for item in items:
    platform = item.get('platform', '')
    platforms[platform] = platforms.get(platform, 0) + 1

print('Platform counts:')
for platform, count in platforms.items():
    print(f"{platform}: {count}")

# 检查小红书数据
xiaohongshu_items = [i for i in items if i.get('platform') == '小红书']
print(f"\nXiaohongshu items: {len(xiaohongshu_items)}")
if xiaohongshu_items:
    print('First 3 xiaohongshu items:')
    for i, item in enumerate(xiaohongshu_items[:3]):
        print(f"{i+1}. {item.get('keyword')} (platform: {item.get('platform')})")