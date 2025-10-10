from database import engine, Base
from models import Project, Character, WorldSetting, Volume, Chapter, AIConfig, PromptTemplate

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

if __name__ == "__main__":
    init_db()
