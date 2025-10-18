
#!/usr/bin/env python3
"""
数据库迁移脚本 - 更新表结构以支持全局AI提供商和提示词模板
"""
import psycopg2
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def migrate_database():
    """迁移数据库结构"""
    try:
        # 获取数据库连接信息
        db_name = os.getenv('DB_NAME', 'storyforge')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '123456')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        
        print(f"连接到数据库: {db_host}:{db_port}/{db_name}")
        
        # 直接连接到PostgreSQL数据库执行DDL
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("开始数据库迁移...")
    
    # 1. 创建新表（如果不存在）
    print("1. 创建AI提供商表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_providers (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            api_key VARCHAR(500),
            base_url VARCHAR(500),
            enabled BOOLEAN DEFAULT TRUE,
            is_system BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    print("2. 创建AI模型表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_models (
            id SERIAL PRIMARY KEY,
            provider_id INTEGER REFERENCES ai_providers(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            model_identifier VARCHAR(255) NOT NULL,
            temperature FLOAT DEFAULT 0.7,
            max_tokens INTEGER DEFAULT 2000,
            is_default BOOLEAN DEFAULT FALSE,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    print("3. 创建提示词模板表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            content TEXT NOT NULL,
            variables JSONB,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    # 2. 修改现有表结构（确保project_id字段为可选）
    print("4. 检查并修改表结构...")
    
    # 确保ai_providers表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_providers (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            api_key VARCHAR(500),
            base_url VARCHAR(500),
            enabled BOOLEAN DEFAULT TRUE,
            is_system BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    # 确保prompt_templates表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            content TEXT NOT NULL,
            variables JSONB,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    # 检查并修改ai_providers表的project_id字段为可选
    cursor.execute("""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'ai_providers' AND column_name = 'project_id';
    """)
    result = cursor.fetchone()
    if result:
        if result[1] == 'NO':
            print("  修改ai_providers表的project_id字段为可选...")
            cursor.execute("ALTER TABLE ai_providers ALTER COLUMN project_id DROP NOT NULL;")
        else:
            print("  ai_providers表的project_id字段已经是可选的")
    else:
        print("  ai_providers表不存在project_id字段")
    
    # 检查并修改prompt_templates表的project_id字段为可选
    cursor.execute("""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'prompt_templates' AND column_name = 'project_id';
    """)
    result = cursor.fetchone()
    if result:
        if result[1] == 'NO':
            print("  修改prompt_templates表的project_id字段为可选...")
            cursor.execute("ALTER TABLE prompt_templates ALTER COLUMN project_id DROP NOT NULL;")
        else:
            print("  prompt_templates表的project_id字段已经是可选的")
    else:
        print("  prompt_templates表不存在project_id字段，将添加该字段...")
        cursor.execute("ALTER TABLE prompt_templates ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE;")
        cursor.execute("ALTER TABLE prompt_templates ALTER COLUMN project_id DROP NOT NULL;")
        print("  已添加并设置prompt_templates表的project_id字段为可选")
    
    # 3. 创建索引
    print("5. 创建索引...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_providers_project_id ON ai_providers(project_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_models_provider_id ON ai_models(provider_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_templates_project_id ON prompt_templates(project_id);")
    
    # 4. 插入默认数据
    print("6. 插入默认数据...")
    
    # 检查是否已存在系统AI提供商
    cursor.execute("SELECT COUNT(*) FROM ai_providers WHERE is_system = TRUE;")
    count = cursor.fetchone()[0]
    if count == 0:
        print("  插入默认系统AI提供商...")
        cursor.execute("""
            INSERT INTO ai_providers (project_id, name, api_key, base_url, enabled, is_system)
            VALUES
            (NULL, 'OpenAI', '', 'https://api.openai.com/v1', true, true),
            (NULL, 'Gemini', '', 'https://generativelanguage.googleapis.com', true, true),
            (NULL, 'Claude', '', 'https://api.anthropic.com', true, true);
        """)
        
        # 获取刚插入的提供商ID
        cursor.execute("SELECT id FROM ai_providers WHERE name IN ('OpenAI', 'Gemini', 'Claude') ORDER BY id;")
        provider_ids = [row[0] for row in cursor.fetchall()]
        
        print("  插入默认AI模型...")
        cursor.execute("""
            INSERT INTO ai_models (provider_id, name, model_identifier, temperature, max_tokens, is_default, enabled)
            VALUES
            (%s, 'GPT-3.5 Turbo', 'gpt-3.5-turbo', 0.7, 2000, true, true),
            (%s, 'GPT-4', 'gpt-4', 0.7, 4000, false, true),
            (%s, 'Gemini Pro', 'gemini-pro', 0.7, 2000, true, true),
            (%s, 'Claude 3 Haiku', 'claude-3-haiku-20240307', 0.7, 2000, true, true);
        """, (provider_ids[0], provider_ids[0], provider_ids[1], provider_ids[2]))
    
    # 检查是否已存在默认提示词模板
    cursor.execute("SELECT COUNT(*) FROM prompt_templates WHERE is_default = TRUE;")
    count = cursor.fetchone()[0]
    if count == 0:
        print("  插入默认提示词模板...")
        cursor.execute("""
            INSERT INTO prompt_templates (project_id, name, category, content, is_default)
            VALUES
            (NULL, '小说创作助手', '创作', '请你扮演一位专业的小说创作助手，帮助作者进行小说创作。请根据以下要求提供创作建议和内容：\n\n{{content}}\n\n请确保内容符合小说的逻辑性和文学性。', true),
            (NULL, '角色设定', '角色', '请帮我完善这个角色设定：\n\n角色名称：{{character_name}}\n基本背景：{{background}}\n\n请提供详细的角色性格、动机、成长轨迹等信息。', true),
            (NULL, '世界观构建', '世界观', '请帮我构建这个奇幻世界的设定：\n\n世界名称：{{world_name}}\n基本特征：{{features}}\n\n请详细描述这个世界的地理、历史、文化、魔法体系等。', true),
            (NULL, '情节发展', '情节', '请帮我设计接下来的情节发展：\n\n当前情节：{{current_plot}}\n期望方向：{{direction}}\n\n请提供具体的情节建议和冲突设置。', true);
        """)
    
    cursor.close()
    conn.close()
    print("数据库迁移完成！")