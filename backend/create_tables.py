
#!/usr/bin/env python3
"""
创建数据库表脚本 - 使用SQLAlchemy自动创建表
"""
from database import engine, Base
from models import Project, Volume, Chapter, AIProvider, AIModel, PromptTemplate, Worldview, RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon, Conversation, Message, NovelGenre
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_tables():
    """创建所有数据库表"""
    try:
        print("开始创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("数据库表创建完成！")
    except Exception as e:
        print(f"数据库表创建失败: {e}")
        import traceback
        traceback.print_exc()