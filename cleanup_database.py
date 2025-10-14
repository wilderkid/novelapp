from sqlalchemy import create_engine, inspect, text
from backend.database import SQLALCHEMY_DATABASE_URL

def cleanup_database():
    """连接到数据库并删除 'characters' 和 'world_settings' 表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    inspector = inspect(engine)

    with engine.connect() as connection:
        if inspector.has_table("characters"):
            print("正在删除 'characters' 表...")
            connection.execute(text("DROP TABLE characters CASCADE"))
            print("'characters' 表已删除。")
        else:
            print("'characters' 表不存在。")

        if inspector.has_table("world_settings"):
            print("正在删除 'world_settings' 表...")
            connection.execute(text("DROP TABLE world_settings CASCADE"))
            print("'world_settings' 表已删除。")
        else:
            print("'world_settings' 表不存在。")

if __name__ == "__main__":
    cleanup_database()