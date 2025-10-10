#!/usr/bin/env python3
"""
测试脚本：验证分卷增加章节功能的修复
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:9009/api"

def test_create_volume_and_chapter():
    """测试创建分卷和章节的功能"""
    print("=== 测试分卷增加章节功能 ===")
    
    try:
        # 1. 获取项目列表
        print("1. 获取项目列表...")
        response = requests.get(f"{BASE_URL}/projects")
        if response.status_code != 200:
            print(f"❌ 获取项目列表失败: {response.status_code}")
            return False
        
        projects = response.json()
        if not projects:
            print("❌ 没有找到项目")
            return False
        
        project_id = projects[0]['id']
        print(f"✅ 找到项目ID: {project_id}")
        
        # 2. 创建分卷
        print("2. 创建分卷...")
        volume_data = {
            "title": "测试分卷",
            "description": "这是一个测试分卷",
            "order": 1,
            "project_id": project_id
        }
        
        response = requests.post(f"{BASE_URL}/volumes", json=volume_data)
        if response.status_code != 200:
            print(f"❌ 创建分卷失败: {response.status_code} - {response.text}")
            return False
        
        volume = response.json()
        volume_id = volume['id']
        print(f"✅ 创建分卷成功，ID: {volume_id}")
        
        # 3. 获取分卷章节列表（测试之前的500错误）
        print("3. 获取分卷章节列表...")
        response = requests.get(f"{BASE_URL}/volumes/{volume_id}/chapters")
        if response.status_code != 200:
            print(f"❌ 获取分卷章节列表失败: {response.status_code} - {response.text}")
            return False
        
        chapters = response.json()
        print(f"✅ 获取分卷章节列表成功，当前章节数: {len(chapters)}")
        
        # 4. 创建章节
        print("4. 创建章节...")
        chapter_data = {
            "title": "测试章节",
            "content": "<p>这是测试章节的内容</p>",
            "word_count": 100,
            "order": 1,
            "volume_id": volume_id
        }
        
        response = requests.post(f"{BASE_URL}/projects/{project_id}/chapters", json=chapter_data)
        if response.status_code != 200:
            print(f"❌ 创建章节失败: {response.status_code} - {response.text}")
            return False
        
        chapter = response.json()
        chapter_id = chapter['id']
        print(f"✅ 创建章节成功，ID: {chapter_id}")
        
        # 5. 再次获取分卷章节列表
        print("5. 再次获取分卷章节列表...")
        response = requests.get(f"{BASE_URL}/volumes/{volume_id}/chapters")
        if response.status_code != 200:
            print(f"❌ 获取分卷章节列表失败: {response.status_code} - {response.text}")
            return False
        
        chapters = response.json()
        print(f"✅ 获取分卷章节列表成功，当前章节数: {len(chapters)}")
        
        if len(chapters) == 1:
            print("✅ 章节创建和关联验证成功")
        else:
            print("❌ 章节创建和关联验证失败")
            return False
        
        print("\n=== 所有测试通过！ ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试分卷增加章节功能...")
    success = test_create_volume_and_chapter()
    if success:
        print("\n🎉 测试通过！分卷增加章节功能已修复")
    else:
        print("\n❌ 测试失败！请检查修复结果")