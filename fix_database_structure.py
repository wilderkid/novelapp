#!/usr/bin/env python3
"""
修复数据库结构脚本：添加缺失的列和约束
"""

import psycopg2

def fix_database_structure():
    """修复数据库结构"""
    print("=== 修复数据库结构 ===")
    
    try:
        # 连接到数据库
        conn = psycopg2.connect(
            host="localhost",
            database="storyforge",
            user="postgres",
            password="123456"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # 0. 删除旧的 ai_configs 表
        print("0. 检查并删除旧的 ai_configs 表...")
        cursor.execute("SELECT to_regclass('public.ai_configs')")
        if cursor.fetchone()[0]:
            print("  找到 ai_configs 表，正在删除...")
            cursor.execute("DROP TABLE ai_configs CASCADE")
            print("  [SUCCESS] ai_configs 表删除成功")
        else:
            print("  ai_configs 表不存在，无需删除")
        
        # 1. 检查并添加 chapters 表的 volume_id 列
        print("1. 检查 chapters 表的 volume_id 列...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chapters' AND column_name = 'volume_id'
        """)
        
        if not cursor.fetchone():
            print("  添加 volume_id 列到 chapters 表...")
            cursor.execute("""
                ALTER TABLE chapters 
                ADD COLUMN volume_id INTEGER REFERENCES volumes(id) ON DELETE CASCADE
            """)
            print("  [SUCCESS] volume_id 列添加成功")
        else:
            print("  volume_id 列已存在")
        
        # 2. 检查并修复列名不一致问题
        print("2. 检查列名不一致问题...")
        
        # 检查 chapters 表的 order 列
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chapters' AND column_name = 'order'
        """)
        
        if not cursor.fetchone():
            print("  将 chapter_order 重命名为 order...")
            cursor.execute("""
                ALTER TABLE chapters 
                RENAME COLUMN chapter_order TO "order"
            """)
            print("  [SUCCESS] chapters 表列名修复成功")
        else:
            print("  chapters 表的 order 列已存在")
        
        # 检查 volumes 表的 order 列
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'volumes' AND column_name = 'order'
        """)
        
        if not cursor.fetchone():
            print("  将 volume_order 重命名为 order...")
            cursor.execute("""
                ALTER TABLE volumes 
                RENAME COLUMN volume_order TO "order"
            """)
            print("  [SUCCESS] volumes 表列名修复成功")
        else:
            print("  volumes 表的 order 列已存在")
        
        # 3. 重新创建索引
        print("3. 重新创建索引...")
        cursor.execute("DROP INDEX IF EXISTS idx_chapters_order")
        cursor.execute("""
            CREATE INDEX idx_chapters_order ON chapters(volume_id, "order")
        """)
        print("  [SUCCESS] 索引重新创建成功")

        # 4. 检查并添加 prompt_templates 表的 project_id 列
        print("4. 检查 prompt_templates 表的 project_id 列...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prompt_templates' AND column_name = 'project_id'
        """)
        if not cursor.fetchone():
            print("  添加 project_id 列到 prompt_templates 表...")
            cursor.execute("""
                ALTER TABLE prompt_templates 
                ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE
            """)
            print("  [SUCCESS] project_id 列添加成功")
        else:
            print("  project_id 列已存在")

        # 5. 检查并添加 ai_providers 表的 is_system 列
        print("5. 检查 ai_providers 表的 is_system 列...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_providers' AND column_name = 'is_system'
        """)
        if not cursor.fetchone():
            print("  添加 is_system 列到 ai_providers 表...")
            cursor.execute("""
                ALTER TABLE ai_providers 
                ADD COLUMN is_system BOOLEAN NOT NULL DEFAULT FALSE
            """)
            print("  [SUCCESS] is_system 列添加成功")
        else:
            print("  is_system 列已存在")

        # 6. 更新 characters 表的结构...
        print("6. 更新 characters 表的结构...")

        # 检查并删除 avatar 列
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'characters' AND column_name = 'avatar'
        """)
        if cursor.fetchone():
            print("  删除 avatar 列从 characters 表...")
            cursor.execute("ALTER TABLE characters DROP COLUMN avatar")
            print("  [SUCCESS] avatar 列删除成功")
        else:
            print("  avatar 列不存在")

        # 检查并删除 details 列
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'characters' AND column_name = 'details'
        """)
        if cursor.fetchone():
            print("  删除 details 列从 characters 表...")
            cursor.execute("ALTER TABLE characters DROP COLUMN details")
            print("  [SUCCESS] details 列删除成功")
        else:
            print("  details 列不存在")

        # 检查并添加 description 列
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'characters' AND column_name = 'description'
        """)
        if not cursor.fetchone():
            print("  添加 description 列到 characters 表...")
            cursor.execute("ALTER TABLE characters ADD COLUMN description TEXT")
            print("  [SUCCESS] description 列添加成功")
        else:
            print("  description 列已存在")

        # 检查并添加 plot 列
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'characters' AND column_name = 'plot'
        """)
        if not cursor.fetchone():
            print("  添加 plot 列到 characters 表...")
            cursor.execute("ALTER TABLE characters ADD COLUMN plot TEXT")
            print("  [SUCCESS] plot 列添加成功")
        else:
            print("  plot 列已存在")

        print("5. 验证修复结果...")
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('chapters', 'volumes')
            AND column_name IN ('volume_id', 'order')
            ORDER BY table_name, column_name
        """)
        
        results = cursor.fetchall()
        print("  修复后的列信息:")
        for row in results:
            print(f"    {row[0]}.{row[1]}: {row[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n=== 数据库结构修复完成 ===")
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库修复失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始修复数据库结构...")
    success = fix_database_structure()
    if success:
        print("\n[SUCCESS] 数据库结构修复成功！")
    else:
        print("\n[ERROR] 数据库结构修复失败！")