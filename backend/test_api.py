#!/usr/bin/env python3
"""
测试API脚本
"""
import requests
import json

def test_apis():
    base_url = "http://localhost:9009"
    
    print("测试AI提供商API...")
    try:
        response = requests.get(f"{base_url}/api/ai-providers")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"AI提供商API测试失败: {e}")
    
    print("\n测试提示词模板API...")
    try:
        response = requests.get(f"{base_url}/api/prompt-templates")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"提示词模板API测试失败: {e}")

if __name__ == "__main__":
    test_apis()