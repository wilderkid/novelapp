#!/usr/bin/env python3
"""
数据库默认数据初始化脚本
在数据库为空时自动插入必要的默认数据
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import NovelGenre
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def init_default_data():
    """初始化默认数据"""
    db = SessionLocal()
    try:
        # 检查并初始化小说类型
        genre_count = db.query(NovelGenre).count()
        if genre_count == 0:
            print("初始化默认小说类型...")
            default_genres = [
                "玄幻", "奇幻", "武侠", "仙侠", "都市",
                "历史", "军事", "游戏", "科幻", "灵异",
                "二次元", "轻小说", "其他"
            ]
            for genre_name in default_genres:
                genre = NovelGenre(name=genre_name)
                db.add(genre)
            db.commit()
            print(f"已添加 {len(default_genres)} 个默认小说类型")
        else:
            print(f"小说类型已存在 ({genre_count} 个)，跳过初始化")
        
        print("默认数据初始化完成！")
        
    except Exception as e:
        print(f"初始化默认数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # 确保表已创建
    Base.metadata.create_all(bind=engine)
    # 初始化默认数据
    init_default_data()