import crawler

# 测试小红书热点采集函数
xhs_data = crawler.fetch_xiaohongshu_hot()
print('Xiaohongshu data count:', len(xhs_data))
if xhs_data:
    print('First item:', xhs_data[0])
    print('Platform:', xhs_data[0]['platform'])