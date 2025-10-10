#!/usr/bin/env python3
"""
数据库诊断脚本：检查数据库表结构
"""

import psycopg2

def check_database_structure():
    """检查数据库结构"""
    print("=== 数据库结构诊断 ===")
    
    try:
        # 连接到数据库
        conn = psycopg2.connect(
            host="localhost",
            database="storyforge",
            user="postgres",
            password="123456"
        )
        cursor = conn.cursor()
        
        # 检查表是否存在
        tables = ['projects', 'characters', 'world_settings', 'volumes', 'chapters']
        
        for table in tables:
            print(f"\n--- 检查表: {table} ---")
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            if columns:
                print(f"表 {table} 存在，列信息:")
                for col in columns:
                    print(f"  {col[0]}: {col[1]} (可空: {col[2]}, 默认值: {col[3]})")
            else:
                print(f"❌ 表 {table} 不存在")
        
        # 检查外键约束
        print("\n--- 检查外键约束 ---")
        cursor.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name, kcu.column_name
        """)
        
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            print("外键约束:")
            for fk in foreign_keys:
                print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
        else:
            print("没有找到外键约束")
        
        # 检查索引
        print("\n--- 检查索引 ---")
        cursor.execute("""
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            print("索引信息:")
            for idx in indexes:
                print(f"  {idx[0]}: {idx[1]}")
        else:
            print("没有找到索引")
        
        cursor.close()
        conn.close()
        
        print("\n=== 诊断完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    check_database_structure()