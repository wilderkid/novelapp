"""
添加 display_order 字段到 projects 表
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def add_display_order_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查列是否已存在
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='projects' AND column_name='display_order'
        """))
        
        if result.fetchone() is None:
            print("添加 display_order 列...")
            conn.execute(text("ALTER TABLE projects ADD COLUMN display_order INTEGER DEFAULT 0"))
            conn.commit()
            print("✓ display_order 列添加成功")
            
            # 为现有项目设置排序值（按 id 排序）
            print("为现有项目设置排序值...")
            conn.execute(text("UPDATE projects SET display_order = id WHERE display_order = 0"))
            conn.commit()
            print("✓ 现有项目排序值设置完成")
        else:
            print("display_order 列已存在，跳过")

if __name__ == "__main__":
    add_display_order_column()