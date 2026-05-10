import crawler

# 测试爬虫函数
result = crawler.fetch_all_hotspots()
print('Total:', result['total'])

# 统计各平台的数量
platforms = {}
for item in result['items']:
    platform = item['platform']
    if platform not in platforms:
        platforms[platform] = 0
    platforms[platform] += 1

print('Platform counts:')
for platform, count in platforms.items():
    print(f"{platform}: {count}")

# 检查小红书数据
xiaohongshu_items = [i for i in result['items'] if i['platform'] == '小红书']
print(f"\nXiaohongshu items: {len(xiaohongshu_items)}")
if xiaohongshu_items:
    print('First 5 xiaohongshu items:')
    for i, item in enumerate(xiaohongshu_items[:5]):
        print(f"{i+1}. {item['keyword']} (hot_value: {item['hot_value']})")