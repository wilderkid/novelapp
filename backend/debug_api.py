#!/usr/bin/env python3
"""
调试API脚本 - 捕获完整错误信息
"""
import requests
import json
import traceback

def debug_api():
    base_url = "http://localhost:9009"
    
    print("=== 调试提示词模板API ===")
    try:
        response = requests.get(f"{base_url}/api/prompt-templates", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code >= 400:
            print(f"错误详情: {response.reason}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"其他异常: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_api()