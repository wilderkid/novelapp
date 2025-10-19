import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取数据库连接配置
# 确保使用PostgreSQL，不使用SQLite
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL环境变量未设置，请确保在.env文件中配置PostgreSQL数据库连接")

def add_project_id_to_prompt_templates():
    """为prompt_templates表添加project_id字段"""

    # 解析数据库URL
    db_url = DATABASE_URL.replace("postgresql://", "")
    db_user, db_password = db_url.split("@")[0].split(":")
    db_host, db_name = db_url.split("@")[1].split("/")

    # 连接数据库
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()

    try:
        # 检查project_id列是否已存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='prompt_templates' AND column_name='project_id'
        """)

        if not cursor.fetchone():
            # 添加project_id列
            cursor.execute("ALTER TABLE prompt_templates ADD COLUMN project_id INTEGER")
            print("已添加project_id列到prompt_templates表")

            # 提交更改
            conn.commit()
        else:
            print("project_id列已存在于prompt_templates表中")

    except Exception as e:
        print(f"添加project_id列时出错: {e}")
        conn.rollback()
    finally:
        # 关闭连接
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_project_id_to_prompt_templates()
