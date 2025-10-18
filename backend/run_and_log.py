#!/usr/bin/env python3
"""
运行后端服务并捕获日志
"""
import subprocess
import sys

def run_server():
    """运行后端服务并显示日志"""
    try:
        # 运行后端服务
        process = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("后端服务启动中...")
        
        # 实时输出日志
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            
    except KeyboardInterrupt:
        print("\n正在停止后端服务...")
        process.terminate()
        process.wait()
        print("后端服务已停止")
    except Exception as e:
        print(f"运行后端服务时出错: {e}")

if __name__ == "__main__":
    run_server()