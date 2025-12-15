import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost/storyforge")

# 解析数据库URL
# 格式: postgresql://username:password@host:port/database
from urllib.parse import urlparse

parsed = urlparse(DATABASE_URL)
username = parsed.username or "postgres"
password = parsed.password or "123456"
host = parsed.hostname or "localhost"
port = parsed.port or 5432
database = parsed.path.lstrip("/") or "storyforge"

try:
    # 连接数据库
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=username,
        password=password
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("正在更新dungeons表结构...")
    
    # 检查content字段是否已存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='dungeons' AND column_name='content'
    """)
    
    if cursor.fetchone():
        print("content字段已存在，跳过迁移")
    else:
        # 重命名description为content
        cursor.execute("ALTER TABLE dungeons RENAME COLUMN description TO content")
        print("✓ 已将description字段重命名为content")
    
    # 添加created_at字段（如果不存在）
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='dungeons' AND column_name='created_at'
    """)
    
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE dungeons ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
        print("✓ 已添加created_at字段")
    else:
        print("created_at字段已存在")
    
    # 添加updated_at字段（如果不存在）
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='dungeons' AND column_name='updated_at'
    """)
    
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE dungeons ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE")
        print("✓ 已添加updated_at字段")
    else:
        print("updated_at字段已存在")
    
    print("\n数据库迁移完成！")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"迁移失败: {e}")
    import traceback
    traceback.print_exc()