#!/usr/bin/env python3
"""
部署检查脚本 - 验证系统能否在空数据库情况下正常启动
"""
import sys
from database import engine, Base, SessionLocal
from models import NovelGenre
from sqlalchemy import inspect

def check_deployment():
    """检查部署状态"""
    print("=" * 60)
    print("开始部署检查...")
    print("=" * 60)
    
    try:
        # 1. 检查数据库连接
        print("\n[1/3] 检查数据库连接...")
        with engine.connect() as conn:
            print("✓ 数据库连接成功")
        
        # 2. 检查并创建表
        print("\n[2/3] 检查数据库表...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"现有表: {existing_tables}")
        
        print("创建缺失的表...")
        Base.metadata.create_all(bind=engine)
        
        updated_tables = inspector.get_table_names()
        print(f"更新后的表: {updated_tables}")
        print("✓ 数据库表检查完成")
        
        # 3. 测试空数据查询
        print("\n[3/3] 测试空数据查询...")
        db = SessionLocal()
        try:
            genres = db.query(NovelGenre).all()
            print(f"✓ 小说类型查询成功，当前数量: {len(genres)}")
        finally:
            db.close()
        
        print("\n" + "=" * 60)
        print("✓ 部署检查通过！系统可以在空数据库情况下正常运行")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ 部署检查失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_deployment()
    sys.exit(0 if success else 1)