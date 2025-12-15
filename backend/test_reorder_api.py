import requests
import json

# 测试排序API
url = "http://localhost:9009/api/ai-providers/reorder"
data = {"provider_ids": [1, 2, 3]}

print("发送请求到:", url)
print("请求数据:", json.dumps(data, indent=2))

try:
    response = requests.put(url, json=data)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")