"""
更新现有数据的 updated_at 字段
确保所有记录都有正确的时间戳
"""
from database import SessionLocal
from models import (
    Project, Volume, Chapter,
    AIProvider, AIModel, PromptTemplate,
    Worldview, RPGCharacter, Organization,
    SupernaturalPower, Weapon, Dungeon, NovelGenre
)
from sqlalchemy import func

def update_timestamps():
    """更新所有现有记录的 updated_at 字段"""
    db = SessionLocal()
    try:
        # 获取所有需要更新的模型
        models = [
            Project, Volume, Chapter,
            AIProvider, AIModel, PromptTemplate,
            Worldview, RPGCharacter, Organization,
            SupernaturalPower, Weapon, Dungeon, NovelGenre
        ]
        
        for model in models:
            # 查找所有 updated_at 为 NULL 的记录
            records = db.query(model).filter(model.updated_at == None).all()
            
            if records:
                print(f"更新 {model.__tablename__} 表中的 {len(records)} 条记录...")
                for record in records:
                    # 将 updated_at 设置为 created_at 的值
                    record.updated_at = record.created_at
                
                db.commit()
                print(f"✓ {model.__tablename__} 表更新完成")
            else:
                print(f"✓ {model.__tablename__} 表无需更新")
        
        print("\n所有时间戳更新完成！")
        
    except Exception as e:
        print(f"更新时间戳时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_timestamps()