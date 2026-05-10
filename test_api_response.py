import requests
import json

# 测试API响应
response = requests.get('http://127.0.0.1:5001/api/hotspots/refresh')
data = response.json()

print('API response status:', data.get('success'))

if data.get('success'):
    items = data.get('data', {}).get('items', [])
    print('Total items:', len(items))
    
    # 统计各平台的数量
    platforms = {}
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
        print('First 5 xiaohongshu items:')
        for i, item in enumerate(xiaohongshu_items[:5]):
            print(f"{i+1}. {item.get('keyword')} (hot_value: {item.get('hot_value')})")