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
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# 世界观相关模式
class WorldviewBase(BaseSchema):
    content: Optional[str] = None

class WorldviewCreate(WorldviewBase):
    pass

class WorldviewResponse(WorldviewBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 角色相关模式
class RPGCharacterBase(BaseSchema):
    name: str
    content: Optional[str] = None

class RPGCharacterCreate(RPGCharacterBase):
    pass

class RPGCharacterResponse(RPGCharacterBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 组织相关模式
class OrganizationBase(BaseSchema):
    name: str
    content: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 超凡之力相关模式
class SupernaturalPowerBase(BaseSchema):
    name: str
    content: Optional[str] = None

class SupernaturalPowerCreate(SupernaturalPowerBase):
    pass

class SupernaturalPowerResponse(SupernaturalPowerBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 兵器相关模式
class WeaponBase(BaseSchema):
    name: str
    content: Optional[str] = None

class WeaponCreate(WeaponBase):
    pass

class WeaponResponse(WeaponBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 副本相关模式
class DungeonBase(BaseSchema):
    name: str
    content: Optional[str] = None

class DungeonCreate(DungeonBase):
    pass

class DungeonResponse(DungeonBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

