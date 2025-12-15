-- 更新dungeons表结构，将description字段改为content，并添加时间戳字段
ALTER TABLE dungeons RENAME COLUMN description TO content;
ALTER TABLE dungeons ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE dungeons ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;