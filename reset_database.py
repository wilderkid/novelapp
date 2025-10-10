#!/usr/bin/env python3
"""
数据库重置脚本：重新创建数据库表结构
"""

import psycopg2
import os
from pathlib import Path

def reset_database():
    """重置数据库"""
    print("=== 重置数据库 ===")
    
    try:
        # 读取SQL文件
        sql_file = Path("database/init.sql")
        if not sql_file.exists():
            print("❌ 找不到数据库初始化文件")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 连接到PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123456"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 删除现有数据库
        print("1. 删除现有数据库...")
        cursor.execute("DROP DATABASE IF EXISTS storyforge")
        print("✅ 删除数据库成功")
        
        # 创建新数据库
        print("2. 创建新数据库...")
        cursor.execute("CREATE DATABASE storyforge")
        print("✅ 创建数据库成功")
        
        cursor.close()
        conn.close()
        
        # 连接到新数据库并执行初始化脚本
        print("3. 执行数据库初始化脚本...")
        conn = psycopg2.connect(
            host="localhost",
            database="storyforge",
            user="postgres",
            password="123456"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 执行SQL脚本
        cursor.execute(sql_content)
        print("✅ 数据库初始化成功")
        
        cursor.close()
        conn.close()
        
        print("\n=== 数据库重置完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 数据库重置失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始重置数据库...")
    success = reset_database()
    if success:
        print("\n🎉 数据库重置成功！")
    else:
        print("\n❌ 数据库重置失败！")