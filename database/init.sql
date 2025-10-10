-- 创建数据库
CREATE DATABASE storyforge;

-- 连接到数据库
\c storyforge;

-- 创建项目表
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    expected_words INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建角色表
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建世界观设定表
CREATE TABLE world_settings (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建分卷表
CREATE TABLE volumes (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建章节表
CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    volume_id INTEGER REFERENCES volumes(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_characters_project_id ON characters(project_id);
CREATE INDEX idx_world_settings_project_id ON world_settings(project_id);
CREATE INDEX idx_volumes_project_id ON volumes(project_id);
CREATE INDEX idx_chapters_project_id ON chapters(project_id);
CREATE INDEX idx_chapters_volume_id ON chapters(volume_id);
CREATE INDEX idx_chapters_order ON chapters(volume_id, "order");

-- 插入示例数据
INSERT INTO projects (title, genre, description, author, expected_words)
VALUES ('示例项目', '奇幻', '这是一个示例项目，用于展示StoryForge的功能', '示例作者', 100000);

-- 获取刚插入的项目ID
-- 假设ID为1
INSERT INTO characters (project_id, name, details)
VALUES
(1, '李昂', '{"personality": ["勇敢", "鲁莽"], "background": "出身普通农家，从小就展现出与众不同的勇气"}'),
(1, '苏晴', '{"personality": ["聪慧", "冷静"], "background": "来自学者世家，博学多才"}');

INSERT INTO world_settings (project_id, name, type, description, details)
VALUES
(1, '霍格沃茨', '地点', '魔法学校，充满神秘与冒险的地方', '{"建立时间": "公元10世纪", "位置": "苏格兰高地"}'),
(1, '魔法部', '组织', '负责管理魔法世界的政府机构', '{"总部位置": "伦敦地下", "领导者": "魔法部长"}');

-- 插入示例分卷
INSERT INTO volumes (project_id, title, description, "order")
VALUES
(1, '第一卷：初入江湖', '主角初入江湖，结识伙伴，开始冒险旅程', 1),
(1, '第二卷：风云变幻', '江湖风波四起，主角面临重大考验', 2);

-- 插入示例章节
INSERT INTO chapters (project_id, volume_id, title, content, word_count, "order")
VALUES
(1, 1, '第一章：开端', '<p>这是第一章的内容...</p>', 150, 1),
(1, 1, '第二章：发展', '<p>这是第二章的内容...</p>', 200, 2),
(1, 2, '第三章：转折', '<p>这是第三章的内容...</p>', 180, 1);
