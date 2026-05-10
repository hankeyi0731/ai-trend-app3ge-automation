import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# 尝试获取小红书热榜页面，解析其中的JavaScript数据
url = 'https://www.xiaohongshu.com/explore/hot'
try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
    print(f'Content length: {len(resp.text)}')

    # 尝试在页面中查找热点数据
    text = resp.text

    # 查找 __INITIAL_STATE__ 或 window.__INITIAL_STATE__
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*;', text)
    if match:
        print('Found INITIAL_STATE')
        data = match.group(1)
        print(f'Data (first 500 chars): {data[:500]}')
    else:
        print('No INITIAL_STATE found')

    # 查找热点相关的JSON数据
    matches = re.findall(r'"hotList":\s*\[(.*?)\]', text)
    if matches:
        print(f'Found hotList: {matches[0][:500]}')

    # 查找其他可能的热点数据
    matches = re.findall(r'"hot":\s*\[(.*?)\]', text)
    if matches:
        print(f'Found hot: {matches[0][:500]}')

except Exception as e:
    print(f'Error: {e}')