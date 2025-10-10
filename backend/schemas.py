from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# 基础模式
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# 项目相关模式
class ProjectBase(BaseSchema):
    title: str
    genre: str
    description: Optional[str] = None
    author: Optional[str] = None
    expected_words: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    word_count: Optional[int] = 0
    chapter_count: Optional[int] = 0

# 角色相关模式
class CharacterBase(BaseSchema):
    name: str
    description: Optional[str] = None
    plot: Optional[str] = None

class CharacterCreate(CharacterBase):
    pass

class CharacterResponse(CharacterBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 世界观相关模式
class WorldSettingBase(BaseSchema):
    name: str
    type: str
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class WorldSettingCreate(WorldSettingBase):
    pass

class WorldSettingResponse(WorldSettingBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 分卷相关模式
class VolumeBase(BaseSchema):
    title: str
    description: Optional[str] = None
    order: Optional[int] = 0

class VolumeCreate(VolumeBase):
    project_id: int

class VolumeResponse(VolumeBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 章节相关模式
class ChapterBase(BaseSchema):
    title: str
    content: Optional[str] = None
    word_count: Optional[int] = 0
    order: Optional[int] = 0
    volume_id: Optional[int] = None

class ChapterCreate(ChapterBase):
    pass

class ChapterResponse(ChapterBase):
    id: int
    project_id: int
    volume_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# AI配置相关模式
class AIConfigBase(BaseSchema):
    name: str
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4096
    is_default: Optional[bool] = False

class AIConfigCreate(AIConfigBase):
    pass

class AIConfigResponse(AIConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 提示词模板相关模式
class PromptTemplateBase(BaseSchema):
    name: str
    category: Optional[str] = None
    content: str
    variables: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = False

class PromptTemplateCreate(PromptTemplateBase):
    pass

class PromptTemplateResponse(PromptTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
