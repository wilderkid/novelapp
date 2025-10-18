-- 更新数据库结构以支持AI提供商和提示词模板
-- 添加AI提供商表
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

-- 添加AI模型表
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

-- 添加提示词模板表
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

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ai_providers_project_id ON ai_providers(project_id);
CREATE INDEX IF NOT EXISTS idx_ai_models_provider_id ON ai_models(provider_id);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_project_id ON prompt_templates(project_id);

-- 插入默认的系统AI提供商
INSERT INTO ai_providers (name, api_key, base_url, enabled, is_system) VALUES
('OpenAI', '', 'https://api.openai.com/v1', true, true),
('Gemini', '', 'https://generativelanguage.googleapis.com', true, true),
('Claude', '', 'https://api.anthropic.com', true, true);

-- 插入默认的系统AI模型
INSERT INTO ai_models (provider_id, name, model_identifier, temperature, max_tokens, is_default, enabled) VALUES
(1, 'GPT-3.5 Turbo', 'gpt-3.5-turbo', 0.7, 2000, true, true),
(1, 'GPT-4', 'gpt-4', 0.7, 4000, false, true),
(2, 'Gemini Pro', 'gemini-pro', 0.7, 2000, false, true),
(3, 'Claude 3 Haiku', 'claude-3-haiku-20240307', 0.7, 2000, false, true);

-- 插入默认的提示词模板
INSERT INTO prompt_templates (name, category, content, is_default) VALUES
('小说创作助手', '创作', '请你扮演一位专业的小说创作助手，帮助作者进行小说创作。请根据以下要求提供创作建议和内容：\n\n{{content}}\n\n请确保内容符合小说的逻辑性和文学性。', true),
('角色设定', '角色', '请帮我完善这个角色设定：\n\n角色名称：{{character_name}}\n基本背景：{{background}}\n\n请提供详细的角色性格、动机、成长轨迹等信息。', true),
('世界观构建', '世界观', '请帮我构建这个奇幻世界的设定：\n\n世界名称：{{world_name}}\n基本特征：{{features}}\n\n请详细描述这个世界的地理、历史、文化、魔法体系等。', true),
('情节发展', '情节', '请帮我设计接下来的情节发展：\n\n当前情节：{{current_plot}}\n期望方向：{{direction}}\n\n请提供具体的情节建议和冲突设置。', true);

-- 更新现有表结构（如果需要）
-- 修改ai_providers表的project_id字段为可选
ALTER TABLE ai_providers 
ALTER COLUMN project_id DROP NOT NULL;

-- 修改prompt_templates表的project_id字段为可选
ALTER TABLE prompt_templates 
ALTER COLUMN project_id DROP NOT NULL;