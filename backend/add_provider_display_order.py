from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def add_display_order_column():
    with engine.connect() as conn:
        # 添加 display_order 列
        try:
            conn.execute(text("ALTER TABLE ai_providers ADD COLUMN display_order INTEGER DEFAULT 0"))
            conn.commit()
            print("✓ 已添加 display_order 列到 ai_providers 表")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate" in error_msg or "已经存在" in str(e):
                print("✓ display_order 列已存在于 ai_providers 表")
            else:
                print(f"✗ 添加列失败: {e}")
                raise
        
        # 为现有记录设置初始排序值
        try:
            conn.execute(text("""
                UPDATE ai_providers 
                SET display_order = id 
                WHERE display_order = 0 OR display_order IS NULL
            """))
            conn.commit()
            print("✓ 已为现有提供商设置初始排序值")
        except Exception as e:
            print(f"✗ 设置初始值失败: {e}")
            raise

if __name__ == "__main__":
    add_display_order_column()
    print("\n数据库迁移完成！")