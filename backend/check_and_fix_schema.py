"""
检查并修复数据库表结构
确保 created_at 和 updated_at 字段有正确的默认值
"""
from sqlalchemy import inspect, text
from database import engine, SessionLocal
from models import Base

def check_and_fix_schema():
    """检查并修复表结构"""
    db = SessionLocal()
    inspector = inspect(engine)
    
    try:
        # 检查 projects 表的列定义
        columns = inspector.get_columns('projects')
        
        print("当前 projects 表的列定义:")
        for col in columns:
            if col['name'] in ['created_at', 'updated_at']:
                print(f"  {col['name']}: {col['type']}, default={col.get('default')}, server_default={col.get('server_default')}")
        
        # 检查是否需要修复
        needs_fix = False
        for col in columns:
            if col['name'] == 'created_at' and not col.get('server_default'):
                needs_fix = True
                print(f"\n⚠️  {col['name']} 缺少 server_default")
            if col['name'] == 'updated_at' and not col.get('server_default'):
                needs_fix = True
                print(f"\n⚠️  {col['name']} 缺少 server_default")
        
        if needs_fix:
            print("\n正在修复表结构...")
            
            # 为 created_at 添加默认值（如果没有）
            try:
                db.execute(text("""
                    ALTER TABLE projects 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP
                """))
                print("✓ 已为 projects.created_at 设置默认值")
            except Exception as e:
                print(f"  created_at 可能已有默认值: {e}")
            
            # 为 updated_at 添加默认值（如果没有）
            try:
                db.execute(text("""
                    ALTER TABLE projects 
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP
                """))
                print("✓ 已为 projects.updated_at 设置默认值")
            except Exception as e:
                print(f"  updated_at 可能已有默认值: {e}")
            
            db.commit()
            print("\n表结构修复完成！")
        else:
            print("\n✓ 表结构正常，无需修复")
            
    except Exception as e:
        print(f"检查表结构时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_schema()