import os
import sys

# 将 backend 目录添加到 sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from models import Chapter, Volume
from database import SQLALCHEMY_DATABASE_URL

def cleanup_orphaned_chapters():
    """
    清理数据库中没有有效 volume_id 的孤儿章节。
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 获取所有现存的 volume ID
        existing_volume_ids = {volume.id for volume in db.query(Volume.id).all()}
        print(f"发现 {len(existing_volume_ids)} 个有效的分卷 ID。")

        # 查找所有章节
        all_chapters = db.query(Chapter).all()
        print(f"数据库中共有 {len(all_chapters)} 个章节。")

        orphaned_chapters = []
        for chapter in all_chapters:
            if chapter.volume_id not in existing_volume_ids:
                orphaned_chapters.append(chapter)

        if not orphaned_chapters:
            print("恭喜！没有发现任何孤儿章节。您的数据是干净的。")
            return

        print(f"发现了 {len(orphaned_chapters)} 个孤儿章节，将进行删除：")
        for chapter in orphaned_chapters:
            print(f"  - 正在删除章节: ID={chapter.id}, 标题='{chapter.title}', 所属的无效分卷ID={chapter.volume_id}")
            db.delete(chapter)
        
        db.commit()
        print(f"成功删除了 {len(orphaned_chapters)} 个孤儿章节。")

    except Exception as e:
        print(f"在清理过程中发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始执行数据库清理脚本...")
    cleanup_orphaned_chapters()
    print("脚本执行完毕。")
