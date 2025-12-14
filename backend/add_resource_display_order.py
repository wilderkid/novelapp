"""
添加 display_order 字段到所有资源表
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def add_resource_display_order():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    tables = ['rpg_characters', 'organizations', 'supernatural_powers', 'weapons', 'dungeons']
    
    with engine.connect() as conn:
        for table in tables:
            # 检查列是否已存在
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='{table}' AND column_name='display_order'
            """))
            
            if result.fetchone() is None:
                print(f"添加 {table}.display_order 列...")
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN display_order INTEGER DEFAULT 0"))
                conn.commit()
                print(f"✓ {table}.display_order 列添加成功")
                
                # 为现有资源设置排序值（按 id 排序）
                print(f"为 {table} 现有资源设置排序值...")
                conn.execute(text(f"UPDATE {table} SET display_order = id WHERE display_order = 0"))
                conn.commit()
                print(f"✓ {table} 现有资源排序值设置完成")
            else:
                print(f"{table}.display_order 列已存在，跳过")

if __name__ == "__main__":
    add_resource_display_order()