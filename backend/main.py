
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
import uvicorn
import os
import json
import aiofiles
import httpx
from typing import List, Optional
from pydantic import BaseModel

from database import SessionLocal, engine, Base
from sqlalchemy import func
from models import (
    Project, Volume, Chapter, 
    AIProvider, AIModel, PromptTemplate, 
    Worldview, RPGCharacter, Organization, 
    SupernaturalPower, Weapon, Dungeon, 
    Conversation, Message
)
from schemas import (
    ProjectCreate, ProjectResponse, 
    VolumeCreate, VolumeResponse,
    ChapterCreate, ChapterResponse,
    AIProviderCreate, AIProviderResponse, AIProviderUpdate,
    AIModelCreate, AIModelResponse, AIModelUpdate,
    PromptTemplateCreate, PromptTemplateResponse,
    WorldviewCreate, WorldviewResponse,
    RPGCharacterCreate, RPGCharacterResponse,
    OrganizationCreate, OrganizationResponse,
    SupernaturalPowerCreate, SupernaturalPowerResponse,
    WeaponCreate, WeaponResponse,
    DungeonCreate, DungeonResponse,
    ConversationResponse, MessageResponse, ConversationUpdate
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# FastAPI应用
app = FastAPI(title="StoryForge API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 项目相关API
@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """获取所有项目"""
    # 使用 joinedload 高效地一次性获取所有项目及其关联的章节
    projects = db.query(Project).options(joinedload(Project.chapters)).all()
    
    # 为每个项目计算字数和章节数统计
    for project in projects:
        # 从已加载的关系中计算统计数据
        project.chapter_count = len(project.chapters)
        project.word_count = sum(c.word_count for c in project.chapters if c.word_count is not None)
    
    return projects

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """创建新项目"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取特定项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    """更新项目"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")

    for key, value in project.dict().items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")

    db.delete(db_project)
    db.commit()
    return {"message": "项目已删除"}







# 分卷相关API
@app.get("/api/projects/{project_id}/volumes", response_model=List[VolumeResponse])
def get_volumes(project_id: int, db: Session = Depends(get_db)):
    """获取项目的所有分卷"""
    volumes = db.query(Volume).filter(Volume.project_id == project_id).all()
    return volumes

@app.post("/api/projects/{project_id}/volumes", response_model=VolumeResponse)
def create_volume(project_id: int, volume: VolumeCreate, db: Session = Depends(get_db)):
    """创建新分卷"""
    volume_data = volume.dict(exclude={"project_id"})
    db_volume = Volume(project_id=project_id, **volume_data)
    db.add(db_volume)
    db.commit()
    db.refresh(db_volume)
    return db_volume

@app.get("/api/volumes/{volume_id}", response_model=VolumeResponse)
def get_volume(volume_id: int, db: Session = Depends(get_db)):
    """获取特定分卷"""
    volume = db.query(Volume).filter(Volume.id == volume_id).first()
    if not volume:
        raise HTTPException(status_code=404, detail="分卷不存在")
    return volume

@app.put("/api/volumes/{volume_id}", response_model=VolumeResponse)
def update_volume(volume_id: int, volume: VolumeCreate, db: Session = Depends(get_db)):
    """更新分卷"""
    db_volume = db.query(Volume).filter(Volume.id == volume_id).first()
    if not db_volume:
        raise HTTPException(status_code=404, detail="分卷不存在")

    for key, value in volume.dict().items():
        setattr(db_volume, key, value)

    db.commit()
    db.refresh(db_volume)
    return db_volume

@app.delete("/api/volumes/{volume_id}")
def delete_volume(volume_id: int, db: Session = Depends(get_db)):
    """删除分卷"""
    db_volume = db.query(Volume).filter(Volume.id == volume_id).first()
    if not db_volume:
        raise HTTPException(status_code=404, detail="分卷不存在")

    # 首先，删除该分卷下的所有章节
    db.query(Chapter).filter(Chapter.volume_id == volume_id).delete(synchronize_session=False)
    
    # 然后，删除分卷本身
    db.delete(db_volume)
    db.commit()
    return {"message": "分卷已删除"}

# 章节相关API
@app.get("/api/volumes/{volume_id}/chapters", response_model=List[ChapterResponse])
def get_chapters(volume_id: int, db: Session = Depends(get_db)):
    """获取分卷的所有章节"""
    chapters = db.query(Chapter).filter(Chapter.volume_id == volume_id).all()
    return chapters

@app.post("/api/volumes/{volume_id}/chapters", response_model=ChapterResponse)
def create_chapter(volume_id: int, chapter: ChapterCreate, db: Session = Depends(get_db)):
    """创建新章节"""
    volume = db.query(Volume).filter(Volume.id == volume_id).first()
    if not volume:
        raise HTTPException(status_code=404, detail="分卷不存在")
    
    chapter_data = chapter.dict(exclude={"volume_id"})
    db_chapter = Chapter(project_id=volume.project_id, volume_id=volume_id, **chapter_data)
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

@app.get("/api/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """获取特定章节"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter

@app.put("/api/chapters/{chapter_id}", response_model=ChapterResponse)
def update_chapter(chapter_id: int, chapter: ChapterCreate, db: Session = Depends(get_db)):
    """更新章节"""
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    update_data = chapter.dict(exclude_unset=True)

    # 如果要移动章节到新的分卷
    if "volume_id" in update_data and update_data["volume_id"] != db_chapter.volume_id:
        new_volume = db.query(Volume).filter(Volume.id == update_data["volume_id"]).first()
        if not new_volume:
            raise HTTPException(status_code=404, detail="新分卷不存在")
        # 同步更新 project_id
        db_chapter.project_id = new_volume.project_id

    for key, value in update_data.items():
        setattr(db_chapter, key, value)

    db.commit()
    db.refresh(db_chapter)
    return db_chapter

@app.delete("/api/chapters/{chapter_id}")
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """删除章节"""
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    db.delete(db_chapter)
    db.commit()
    return {"message": "章节已删除"}

# AI 提供商相关 API - 全局级别
@app.get("/api/ai-providers", response_model=List[AIProviderResponse])
def get_global_ai_providers(db: Session = Depends(get_db)):
    """获取所有AI提供商（全局级别）"""
    providers = db.query(AIProvider).all()
    return providers

@app.post("/api/ai-providers", response_model=AIProviderResponse)
def create_global_ai_provider(provider: AIProviderCreate, db: Session = Depends(get_db)):
    """创建新的AI提供商（全局级别）"""
    db_provider = AIProvider(**provider.model_dump(), project_id=None)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

# AI 提供商相关 API - 项目级别（保持原有功能）
@app.get("/api/ai-providers", response_model=List[AIProviderResponse])
def get_ai_providers(db: Session = Depends(get_db)):
    """获取所有AI提供商"""
    providers = db.query(AIProvider).all()
    return providers

@app.post("/api/ai-providers", response_model=AIProviderResponse)
def create_ai_provider(provider: AIProviderCreate, db: Session = Depends(get_db)):
    """创建新的AI提供商"""
    db_provider = AIProvider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@app.put("/api/ai-providers/{provider_id}", response_model=AIProviderResponse)
def update_ai_provider(provider_id: int, provider: AIProviderUpdate, db: Session = Depends(get_db)):
    """更新AI提供商"""
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="AI提供商不存在")

    update_data = provider.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_provider, key, value)

    db.commit()
    db.refresh(db_provider)
    return db_provider

@app.delete("/api/ai-providers/{provider_id}")
def delete_ai_provider(provider_id: int, db: Session = Depends(get_db)):
    """删除AI提供商"""
    db_provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="AI提供商不存在")

    db.delete(db_provider)
    db.commit()
    return {"message": "AI提供商已删除"}

# AI 模型相关 API
@app.get("/api/ai-providers/{provider_id}/ai-models", response_model=List[AIModelResponse])
def get_ai_models_for_provider(provider_id: int, db: Session = Depends(get_db)):
    """获取特定AI提供商的所有模型"""
    models = db.query(AIModel).filter(AIModel.provider_id == provider_id).all()
    return models

@app.post("/api/ai-providers/{provider_id}/ai-models", response_model=AIModelResponse)
def create_ai_model(provider_id: int, model: AIModelCreate, db: Session = Depends(get_db)):
    """为AI提供商创建新的模型配置"""
    db_model = AIModel(**model.model_dump(), provider_id=provider_id)
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@app.put("/api/ai-models/{model_id}", response_model=AIModelResponse)
def update_ai_model(model_id: int, model: AIModelUpdate, db: Session = Depends(get_db)):
    """更新AI模型配置"""
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="AI模型不存在")

    update_data = model.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)
    return db_model

@app.delete("/api/ai-models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db)):
    """删除AI模型配置"""
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="AI模型不存在")

    db.delete(db_model)
    db.commit()
    return {"message": "AI模型已删除"}

# 获取所有AI模型（包括其提供商信息）- 全局级别
@app.get("/api/ai-models", response_model=List[AIModelResponse])
def get_all_ai_models(db: Session = Depends(get_db)):
    """获取所有AI模型（包括其提供商信息）"""
    # Get all models from all providers
    models = db.query(AIModel).join(AIProvider).all()
    return models


# 提示模板相关API - 全局级别
@app.get("/api/prompt-templates", response_model=List[PromptTemplateResponse])
def get_global_prompt_templates(db: Session = Depends(get_db)):
    """获取所有提示模板（全局级别）"""
    try:
        # 获取所有提示词模板，包括全局和项目级别的
        templates = db.query(PromptTemplate).all()
        return templates
    except Exception as e:
        print(f"DEBUG: 查询全局提示词模板时出错: {str(e)}")
        print(f"DEBUG: 错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.post("/api/prompt-templates", response_model=PromptTemplateResponse)
def create_global_prompt_template(template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """创建新的提示模板（全局级别）"""
    # 创建全局提示词模板，不设置project_id
    db_template = PromptTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

# 提示模板相关API - 项目级别（不再支持，因为PromptTemplate已移除project_id字段）
@app.get("/api/projects/{project_id}/prompt-templates", response_model=List[PromptTemplateResponse])
def get_prompt_templates(project_id: int, db: Session = Depends(get_db)):
    """获取项目的所有提示模板（已弃用，返回所有全局提示词模板）"""
    templates = db.query(PromptTemplate).all()
    return templates

@app.post("/api/projects/{project_id}/prompt-templates", response_model=PromptTemplateResponse)
def create_prompt_template(project_id: int, template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """创建新的提示模板（已弃用，创建全局提示词模板）"""
    db_template = PromptTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@app.put("/api/prompt-templates/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(template_id: int, template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """更新提示模板"""
    db_template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="提示模板不存在")

    # 更新模板内容，不修改project_id
    update_data = template.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)

    db.commit()
    db.refresh(db_template)
    return db_template

@app.delete("/api/prompt-templates/{template_id}")
def delete_prompt_template(template_id: int, db: Session = Depends(get_db)):
    """删除提示模板"""
    db_template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="提示模板不存在")

    db.delete(db_template)
    db.commit()
    return {"message": "提示模板已删除"}


# 资源管理API

# 世界观 (Worldview)
@app.get("/api/projects/{project_id}/worldview", response_model=WorldviewResponse)
def get_worldview(project_id: int, db: Session = Depends(get_db)):
    """获取项目的世界观"""
    worldview = db.query(Worldview).filter(Worldview.project_id == project_id).first()
    if not worldview:
        # 如果不存在，为该项目创建一个空的世界观
        db_worldview = Worldview(project_id=project_id, content="")
        db.add(db_worldview)
        db.commit()
        db.refresh(db_worldview)
        return db_worldview
    return worldview

@app.put("/api/projects/{project_id}/worldview", response_model=WorldviewResponse)
def update_worldview(project_id: int, worldview: WorldviewCreate, db: Session = Depends(get_db)):
    """更新项目的世界观"""
    db_worldview = db.query(Worldview).filter(Worldview.project_id == project_id).first()
    if not db_worldview:
        raise HTTPException(status_code=404, detail="世界观不存在")
    
    db_worldview.content = worldview.content
    db.commit()
    db.refresh(db_worldview)
    return db_worldview

# 角色 (RPGCharacter)
@app.get("/api/projects/{project_id}/rpg_characters", response_model=List[RPGCharacterResponse])
def get_rpg_characters(project_id: int, db: Session = Depends(get_db)):
    """获取项目的所有角色"""
    return db.query(RPGCharacter).filter(RPGCharacter.project_id == project_id).all()

@app.post("/api/projects/{project_id}/rpg_characters", response_model=RPGCharacterResponse)
def create_rpg_character(project_id: int, character: RPGCharacterCreate, db: Session = Depends(get_db)):
    """为项目创建新角色"""
    db_character = RPGCharacter(project_id=project_id, **character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@app.get("/api/rpg_characters/{character_id}", response_model=RPGCharacterResponse)
def get_rpg_character(character_id: int, db: Session = Depends(get_db)):
    """获取特定角色"""
    character = db.query(RPGCharacter).filter(RPGCharacter.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    return character

@app.put("/api/rpg_characters/{character_id}", response_model=RPGCharacterResponse)
def update_rpg_character(character_id: int, character: RPGCharacterCreate, db: Session = Depends(get_db)):
    """更新特定角色"""
    db_character = db.query(RPGCharacter).filter(RPGCharacter.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="角色不存在")
    for key, value in character.dict().items():
        setattr(db_character, key, value)
    db.commit()
    db.refresh(db_character)
    return db_character

@app.delete("/api/rpg_characters/{character_id}")
def delete_rpg_character(character_id: int, db: Session = Depends(get_db)):
    """删除特定角色"""
    db_character = db.query(RPGCharacter).filter(RPGCharacter.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="角色不存在")
    db.delete(db_character)
    db.commit()
    return {"message": "角色已删除"}

# 组织 (Organization)
@app.get("/api/projects/{project_id}/organizations", response_model=List[OrganizationResponse])
def get_organizations(project_id: int, db: Session = Depends(get_db)):
    return db.query(Organization).filter(Organization.project_id == project_id).all()

@app.post("/api/projects/{project_id}/organizations", response_model=OrganizationResponse)
def create_organization(project_id: int, organization: OrganizationCreate, db: Session = Depends(get_db)):
    db_organization = Organization(project_id=project_id, **organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization

@app.get("/api/organizations/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="组织不存在")
    return organization

@app.put("/api/organizations/{organization_id}", response_model=OrganizationResponse)
def update_organization(organization_id: int, organization: OrganizationCreate, db: Session = Depends(get_db)):
    db_organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not db_organization:
        raise HTTPException(status_code=404, detail="组织不存在")
    for key, value in organization.dict().items():
        setattr(db_organization, key, value)
    db.commit()
    db.refresh(db_organization)
    return db_organization

@app.delete("/api/organizations/{organization_id}")
def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    db_organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not db_organization:
        raise HTTPException(status_code=404, detail="组织不存在")
    db.delete(db_organization)
    db.commit()
    return {"message": "组织已删除"}

# 超凡之力 (SupernaturalPower)
@app.get("/api/projects/{project_id}/supernatural_powers", response_model=List[SupernaturalPowerResponse])
def get_supernatural_powers(project_id: int, db: Session = Depends(get_db)):
    return db.query(SupernaturalPower).filter(SupernaturalPower.project_id == project_id).all()

@app.post("/api/projects/{project_id}/supernatural_powers", response_model=SupernaturalPowerResponse)
def create_supernatural_power(project_id: int, power: SupernaturalPowerCreate, db: Session = Depends(get_db)):
    db_power = SupernaturalPower(project_id=project_id, **power.dict())
    db.add(db_power)
    db.commit()
    db.refresh(db_power)
    return db_power

@app.get("/api/supernatural_powers/{power_id}", response_model=SupernaturalPowerResponse)
def get_supernatural_power(power_id: int, db: Session = Depends(get_db)):
    power = db.query(SupernaturalPower).filter(SupernaturalPower.id == power_id).first()
    if not power:
        raise HTTPException(status_code=404, detail="超凡之力不存在")
    return power

@app.put("/api/supernatural_powers/{power_id}", response_model=SupernaturalPowerResponse)
def update_supernatural_power(power_id: int, power: SupernaturalPowerCreate, db: Session = Depends(get_db)):
    db_power = db.query(SupernaturalPower).filter(SupernaturalPower.id == power_id).first()
    if not db_power:
        raise HTTPException(status_code=404, detail="超凡之力不存在")
    for key, value in power.dict().items():
        setattr(db_power, key, value)
    db.commit()
    db.refresh(db_power)
    return db_power

@app.delete("/api/supernatural_powers/{power_id}")
def delete_supernatural_power(power_id: int, db: Session = Depends(get_db)):
    db_power = db.query(SupernaturalPower).filter(SupernaturalPower.id == power_id).first()
    if not db_power:
        raise HTTPException(status_code=404, detail="超凡之力不存在")
    db.delete(db_power)
    db.commit()
    return {"message": "超凡之力已删除"}

# 兵器 (Weapon)
@app.get("/api/projects/{project_id}/weapons", response_model=List[WeaponResponse])
def get_weapons(project_id: int, db: Session = Depends(get_db)):
    return db.query(Weapon).filter(Weapon.project_id == project_id).all()

@app.post("/api/projects/{project_id}/weapons", response_model=WeaponResponse)
def create_weapon(project_id: int, weapon: WeaponCreate, db: Session = Depends(get_db)):
    db_weapon = Weapon(project_id=project_id, **weapon.dict())
    db.add(db_weapon)
    db.commit()
    db.refresh(db_weapon)
    return db_weapon

@app.get("/api/weapons/{weapon_id}", response_model=WeaponResponse)
def get_weapon(weapon_id: int, db: Session = Depends(get_db)):
    weapon = db.query(Weapon).filter(Weapon.id == weapon_id).first()
    if not weapon:
        raise HTTPException(status_code=404, detail="兵器不存在")
    return weapon

@app.put("/api/weapons/{weapon_id}", response_model=WeaponResponse)
def update_weapon(weapon_id: int, weapon: WeaponCreate, db: Session = Depends(get_db)):
    db_weapon = db.query(Weapon).filter(Weapon.id == weapon_id).first()
    if not db_weapon:
        raise HTTPException(status_code=404, detail="兵器不存在")
    for key, value in weapon.dict().items():
        setattr(db_weapon, key, value)
    db.commit()
    db.refresh(db_weapon)
    return db_weapon

@app.delete("/api/weapons/{weapon_id}")
def delete_weapon(weapon_id: int, db: Session = Depends(get_db)):
    db_weapon = db.query(Weapon).filter(Weapon.id == weapon_id).first()
    if not db_weapon:
        raise HTTPException(status_code=404, detail="兵器不存在")
    db.delete(db_weapon)
    db.commit()
    return {"message": "兵器已删除"}

# 副本 (Dungeon)
@app.get("/api/projects/{project_id}/dungeons", response_model=List[DungeonResponse])
def get_dungeons(project_id: int, db: Session = Depends(get_db)):
    return db.query(Dungeon).filter(Dungeon.project_id == project_id).all()

@app.post("/api/projects/{project_id}/dungeons", response_model=DungeonResponse)
def create_dungeon(project_id: int, dungeon: DungeonCreate, db: Session = Depends(get_db)):
    db_dungeon = Dungeon(project_id=project_id, **dungeon.dict())
    db.add(db_dungeon)
    db.commit()
    db.refresh(db_dungeon)
    return db_dungeon

@app.get("/api/dungeons/{dungeon_id}", response_model=DungeonResponse)
def get_dungeon(dungeon_id: int, db: Session = Depends(get_db)):
    dungeon = db.query(Dungeon).filter(Dungeon.id == dungeon_id).first()
    if not dungeon:
        raise HTTPException(status_code=404, detail="副本不存在")
    return dungeon

@app.put("/api/dungeons/{dungeon_id}", response_model=DungeonResponse)
def update_dungeon(dungeon_id: int, dungeon: DungeonCreate, db: Session = Depends(get_db)):
    db_dungeon = db.query(Dungeon).filter(Dungeon.id == dungeon_id).first()
    if not db_dungeon:
        raise HTTPException(status_code=404, detail="副本不存在")
    for key, value in dungeon.dict().items():
        setattr(db_dungeon, key, value)
    db.commit()
    db.refresh(db_dungeon)
    return db_dungeon

@app.delete("/api/dungeons/{dungeon_id}")
def delete_dungeon(dungeon_id: int, db: Session = Depends(get_db)):
    db_dungeon = db.query(Dungeon).filter(Dungeon.id == dungeon_id).first()
    if not db_dungeon:
        raise HTTPException(status_code=404, detail="副本不存在")
    db.delete(db_dungeon)
    db.commit()
    return {"message": "副本已删除"}

# Conversation History API
@app.get("/api/conversations", response_model=List[ConversationResponse])
def get_conversations_for_project(db: Session = Depends(get_db)):
    """获取所有全局对话历史记录（不含消息内容）"""
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).all()
    # 为了效率，我们不在此处返回完整的消息列表
    for conv in conversations:
        conv.messages = [] # 清空消息列表
    return conversations

@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages_for_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """获取特定对话的所有消息"""
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    if not messages:
        # 即使对话存在但没有消息，也返回空列表，而不是404
        # 但要检查对话是否存在
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
    return messages




@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """删除特定对话及其所有消息"""
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not db_conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    db.delete(db_conversation)
    db.commit()
    return {"message": "对话已删除"}

@app.put("/api/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(conversation_id: int, conversation_update: ConversationUpdate, db: Session = Depends(get_db)):
    """更新特定对话的标题"""
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not db_conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    db_conversation.title = conversation_update.title
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

# 提示词渲染API
@app.post("/api/prompts/render")
def render_prompt(payload: dict, db: Session = Depends(get_db)):
    import re
    content = payload.get("content", "")
    project_id = payload.get("project_id")

    # 如果没有提供项目ID，直接返回原始内容，不进行渲染
    # AI功能是全局的，渲染可能用于特定项目上下文，但不是必需的
    if not project_id:
        return {"rendered_content": content}

    keywords = re.findall(r"\{\{\s*(.*?)\s*\}\}", content)
    if not keywords:
        return {"rendered_content": content}

    # 数据源模型列表
    # The order determines precedence if names are duplicated across tables.
    search_models = [
        RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon, Chapter, Volume, Project
    ]

    for keyword in set(keywords):
        found_content = None
        for model in search_models:
            query_attr = 'name' if hasattr(model, 'name') else 'title'
            result = db.query(model).filter(
                getattr(model, 'project_id', None) == project_id, 
                getattr(model, query_attr) == keyword
            ).first()
            
            if result:
                if hasattr(result, 'content') and result.content:
                    found_content = result.content
                elif hasattr(result, 'description') and result.description:
                    found_content = result.description
                else: # Fallback to name/title itself if no content/description
                    found_content = getattr(result, query_attr, '')
                break # Stop searching once a match is found
        
        if found_content:
            content = content.replace(f"{{{{ {keyword} }}}}", found_content)

    return {"rendered_content": content}


class ChatRequest(BaseModel):
    message: str
    # 移除project_id参数，AI对话功能不依赖项目
    conversation_id: Optional[int] = None
    history: List[dict] = []
    prompt_template_id: Optional[int] = None
    ai_model_id: Optional[int] = None
    # 添加resources字段，用于传递提示词中需要的变量值
    resources: Optional[dict] = None

@app.post("/api/chat")
def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """原有的非流式AI对话API，保持向后兼容"""
    conversation_id = request.conversation_id
    system_prompt = None
    selected_ai_model_identifier = "default_model"

    # 获取AI模型和提供商信息
    selected_ai_model = None
    selected_ai_provider = None

    if request.prompt_template_id:
        prompt_template = db.query(PromptTemplate).filter(PromptTemplate.id == request.prompt_template_id).first()
        if prompt_template:
            # 使用新的提示词处理函数
            from prompt_utils import process_prompt_template
            system_prompt = process_prompt_template(db, prompt_template, request.resources)

    if request.ai_model_id:
        selected_ai_model = db.query(AIModel).filter(AIModel.id == request.ai_model_id).first()
        if selected_ai_model:
            selected_ai_model_identifier = selected_ai_model.model_identifier
            selected_ai_provider = db.query(AIProvider).filter(AIProvider.id == selected_ai_model.provider_id).first()
            if not selected_ai_provider:
                raise HTTPException(status_code=404, detail="AI提供商不存在")

    # 如果是新对话，则创建对话记录
    if conversation_id is None:
        # 自动生成标题：取消息的前30个字符
        title = request.message[:30] + '...' if len(request.message) > 30 else request.message
        # AI对话功能不依赖项目，不设置project_id
        new_conv = Conversation(title=title)
        db.add(new_conv)
        db.commit()
        db.refresh(new_conv)
        conversation_id = new_conv.id

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role='user',
        content=request.message
    )
    db.add(user_message)
    db.commit()

    # ---- AI 调用逻辑 ----
    ai_reply_content = "抱歉，AI服务暂不可用或配置不正确。"

    if selected_ai_provider and selected_ai_model:
        # Check if API key is provided
        if not selected_ai_provider.api_key or selected_ai_provider.api_key.strip() == "":
            ai_reply_content = f"AI提供商的API密钥未设置。请在AI管理中配置API密钥。"
        else:
            # 准备消息历史，包括系统提示
            messages_for_ai = []
            if system_prompt:
                messages_for_ai.append({"role": "system", "content": system_prompt})
                # 输出最终使用的提示词
                print("="*50)
                print("最终使用的提示词:")
                print(system_prompt)
                print("="*50)

            # 添加历史消息
            for msg in request.history:
                messages_for_ai.append({"role": msg["role"], "content": msg["content"]})

            # 添加当前用户消息
            messages_for_ai.append({"role": "user", "content": request.message})

            # 动态选择AI客户端并调用 - 使用HTTP请求调用配置的AI服务
            print(f"Debug: Attempting to call AI provider: {selected_ai_provider.name}")
            print(f"Debug: Using model: {selected_ai_model.model_identifier}")
            print(f"Debug: API key is set: {bool(selected_ai_provider.api_key)}")
            print(f"Debug: Base URL: {selected_ai_provider.base_url}")

            try:
                # Default to OpenAI-compatible API if no base_url is provided
                base_url = selected_ai_provider.base_url or "https://api.openai.com/v1"
                api_key = selected_ai_provider.api_key

                if not api_key:
                    ai_reply_content = "AI提供商的API密钥未设置。请在AI管理中配置API密钥。"
                else:
                    # Prepare headers for the API call
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }

                    # Prepare the payload for the AI API call
                    payload = {
                        "model": selected_ai_model.model_identifier,
                        "messages": messages_for_ai,
                        "temperature": selected_ai_model.temperature,
                        "max_tokens": selected_ai_model.max_tokens,
                    }

                    # Determine the correct endpoint URL
                    # For most OpenAI-compatible APIs, it's chat/completions
                    api_endpoint = f"{base_url.rstrip('/')}/chat/completions"

                    # 添加详细的调用日志
                    import datetime
                    import json
                    print("=" * 80)
                    print("【AI调用详细日志】")
                    print(f"调用时间: {datetime.datetime.now()}")
                    print(f"提供商名称: {selected_ai_provider.name}")
                    print(f"API基础URL: {base_url}")
                    print(f"API端点: {api_endpoint}")
                    print(f"模型名称: {selected_ai_model.name}")
                    print(f"模型标识符: {selected_ai_model.model_identifier}")
                    print(f"API密钥: {api_key[:10]}..." if len(api_key) > 10 else f"API密钥: {api_key}")
                    print(f"温度参数: {selected_ai_model.temperature}")
                    print(f"最大Token数: {selected_ai_model.max_tokens}")
                    print("请求载荷:")
                    print(json.dumps(payload, indent=2, ensure_ascii=False))
                    print("=" * 80)

                    # Make the HTTP request to the AI provider
                    import requests
                    response = requests.post(
                        api_endpoint,
                        json=payload,
                        headers=headers,
                        timeout=30.0  # 30 second timeout
                    )

                    print(f"响应状态码: {response.status_code}")

                    if response.status_code == 200:
                        response_data = response.json()
                        ai_reply_content = response_data['choices'][0]['message']['content']
                        print("响应内容:")
                        print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    elif response.status_code == 401:
                        ai_reply_content = f"API密钥无效或已过期。错误代码: {response.status_code}"
                        print(f"错误详情: {response.text}")
                    elif response.status_code == 404:
                        ai_reply_content = f"API端点未找到。请检查API URL是否正确。错误代码: {response.status_code}"
                        print(f"错误详情: {response.text}")
                    elif response.status_code == 429:
                        ai_reply_content = f"API请求频率超限。错误代码: {response.status_code}"
                        print(f"错误详情: {response.text}")
                    else:
                        error_detail = response.text
                        ai_reply_content = f"AI服务调用失败。状态码: {response.status_code}, 详情: {error_detail}"
                        print(f"错误详情: {response.text}")

                    print("=" * 80)

            except Exception as e:
                import traceback
                traceback.print_exc() # Print full traceback to backend logs
                print(f"Debug: AI call failed - {type(e).__name__}: {str(e)}")
                ai_reply_content = f"AI服务调用失败: {type(e).__name__}: {str(e)}"
    else:
        ai_reply_content = f"AI服务未配置。请在AI管理中选择一个AI模型。"

    # ---------------------

    # 保存AI消息
    ai_message = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=ai_reply_content
    )
    db.add(ai_message)
    db.commit()

    return {"reply": ai_reply_content, "conversation_id": conversation_id}

@app.post("/api/chat/stream")
def chat_with_ai_stream(request: ChatRequest, db: Session = Depends(get_db)):
    conversation_id = request.conversation_id
    system_prompt = None
    selected_ai_model_identifier = "default_model"

    # 获取AI模型和提供商信息
    selected_ai_model = None
    selected_ai_provider = None

    if request.prompt_template_id:
        prompt_template = db.query(PromptTemplate).filter(PromptTemplate.id == request.prompt_template_id).first()
        if prompt_template:
            # 使用新的提示词处理函数
            from prompt_utils import process_prompt_template
            system_prompt = process_prompt_template(db, prompt_template, request.resources)

    if request.ai_model_id:
        selected_ai_model = db.query(AIModel).filter(AIModel.id == request.ai_model_id).first()
        if selected_ai_model:
            selected_ai_model_identifier = selected_ai_model.model_identifier
            selected_ai_provider = db.query(AIProvider).filter(AIProvider.id == selected_ai_model.provider_id).first()
            if not selected_ai_provider:
                raise HTTPException(status_code=404, detail="AI提供商不存在")

    # 如果是新对话，则创建对话记录
    if conversation_id is None:
        # 自动生成标题：取消息的前30个字符
        title = request.message[:30] + '...' if len(request.message) > 30 else request.message
        # AI对话功能不依赖项目，不设置project_id
        new_conv = Conversation(title=title)
        db.add(new_conv)
        db.commit()
        db.refresh(new_conv)
        conversation_id = new_conv.id

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role='user',
        content=request.message
    )
    db.add(user_message)
    db.commit()

    async def generate_stream():
        # 导入json模块，确保在嵌套函数中可用
        import json

        # 先发送对话ID，使前端能够保存消息
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id})}\n\n"

        # 初始化AI回复内容
        ai_reply_content = ""

        # 如果没有配置AI提供商或模型，返回错误信息
        if not selected_ai_provider or not selected_ai_model:
            error_msg = "AI服务未配置。请在AI管理中选择一个AI模型。"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

            # 保存错误消息到数据库
            ai_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=error_msg
            )
            db.add(ai_message)
            db.commit()
            return

        # 检查API密钥
        if not selected_ai_provider.api_key or selected_ai_provider.api_key.strip() == "":
            error_msg = "AI提供商的API密钥未设置。请在AI管理中配置API密钥。"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

            # 保存错误消息到数据库
            ai_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=error_msg
            )
            db.add(ai_message)
            db.commit()
            return

        # 准备消息历史，包括系统提示
        messages_for_ai = []
        if system_prompt:
            messages_for_ai.append({"role": "system", "content": system_prompt})
            # 输出最终使用的提示词
            print("="*50)
            print("最终使用的提示词:")
            print(system_prompt)
            print("="*50)

        # 添加历史消息
        for msg in request.history:
            messages_for_ai.append({"role": msg["role"], "content": msg["content"]})

        # 添加当前用户消息
        messages_for_ai.append({"role": "user", "content": request.message})

        # 准备API请求
        base_url = selected_ai_provider.base_url or "https://api.openai.com/v1"
        api_key = selected_ai_provider.api_key
        api_endpoint = f"{base_url.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 准备请求载荷，启用流式响应
        payload = {
            "model": selected_ai_model.model_identifier,
            "messages": messages_for_ai,
            "temperature": selected_ai_model.temperature,
            "max_tokens": selected_ai_model.max_tokens,
            "stream": True  # 启用流式响应
        }

        # 使用httpx进行异步请求，支持流式响应
        import httpx

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    api_endpoint,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"AI服务调用失败。状态码: {response.status_code}, 详情: {error_text.decode()}"
                        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

                        # 保存错误消息到数据库
                        ai_message = Message(
                            conversation_id=conversation_id,
                            role='assistant',
                            content=error_msg
                        )
                        db.add(ai_message)
                        db.commit()
                        return

                    # 处理流式响应
                    async for line in response.aiter_lines():
                        if line:
                            # OpenAI的流式响应以"data: "开头
                            if line.startswith("data: "):
                                data_str = line[6:]  # 移除"data: "前缀

                                # 检查是否是结束标记
                                if data_str.strip() == "[DONE]":
                                    break

                                try:
                                    data = json.loads(data_str)

                                    # 提取内容片段
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("delta", {})
                                        if "content" in delta:
                                            content_chunk = delta["content"]
                                            ai_reply_content += content_chunk

                                            # 发送内容片段到前端
                                            yield f"data: {json.dumps({'type': 'content', 'content': content_chunk})}\n\n"
                                except json.JSONDecodeError:
                                    # 忽略无法解析的JSON行
                                    pass

                    # 流式响应结束，保存完整的AI回复到数据库
                    ai_message = Message(
                        conversation_id=conversation_id,
                        role='assistant',
                        content=ai_reply_content
                    )
                    db.add(ai_message)
                    db.commit()

                    # 发送完成信号
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            error_msg = f"AI服务调用失败: {type(e).__name__}: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

            # 保存错误消息到数据库
            ai_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=error_msg
            )
            db.add(ai_message)
            db.commit()

    # 返回流式响应
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )

    # ---- AI 调用逻辑 ----
    ai_reply_content = "抱歉，AI服务暂不可用或配置不正确。"

    if selected_ai_provider and selected_ai_model:
        # Check if API key is provided
        if not selected_ai_provider.api_key or selected_ai_provider.api_key.strip() == "":
            ai_reply_content = f"AI提供商的API密钥未设置。请在AI管理中配置API密钥。"
        else:
            # 准备消息历史，包括系统提示
            messages_for_ai = []
            if system_prompt:
                messages_for_ai.append({"role": "system", "content": system_prompt})
            
            # 添加历史消息
            for msg in request.history:
                messages_for_ai.append({"role": msg["role"], "content": msg["content"]})
            
            # 添加当前用户消息
            messages_for_ai.append({"role": "user", "content": request.message})

            # 动态选择AI客户端并调用 - 使用HTTP请求调用配置的AI服务
            print(f"Debug: Attempting to call AI provider: {selected_ai_provider.name}")
            print(f"Debug: Using model: {selected_ai_model.model_identifier}")
            print(f"Debug: API key is set: {bool(selected_ai_provider.api_key)}")
            print(f"Debug: Base URL: {selected_ai_provider.base_url}")
            
            try:
                # Default to OpenAI-compatible API if no base_url is provided
                base_url = selected_ai_provider.base_url or "https://api.openai.com/v1"
                api_key = selected_ai_provider.api_key
                
                if not api_key:
                    ai_reply_content = "AI提供商的API密钥未设置。请在AI管理中配置API密钥。"
                else:
                    # Prepare headers for the API call
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }
                    
                    # Prepare the payload for the AI API call
                    payload = {
                        "model": selected_ai_model.model_identifier,
                        "messages": messages_for_ai,
                        "temperature": selected_ai_model.temperature,
                        "max_tokens": selected_ai_model.max_tokens,
                    }
                    
                    # Determine the correct endpoint URL
                    # For most OpenAI-compatible APIs, it's chat/completions
                    api_endpoint = f"{base_url.rstrip('/')}/chat/completions"
                    
                    # 添加详细的调用日志
                    import datetime
                    import json
                    print("=" * 80)
                    print("【AI调用详细日志】")
                    print(f"调用时间: {datetime.datetime.now()}")
                    print(f"提供商名称: {selected_ai_provider.name}")
                    print(f"API基础URL: {base_url}")
                    print(f"API端点: {api_endpoint}")
                    print(f"模型名称: {selected_ai_model.name}")
                    print(f"模型标识符: {selected_ai_model.model_identifier}")
                    print(f"API密钥: {api_key[:10]}..." if len(api_key) > 10 else f"API密钥: {api_key}")
                    print(f"温度参数: {selected_ai_model.temperature}")
                    print(f"最大Token数: {selected_ai_model.max_tokens}")
                    print("请求载荷:")
                    print(json.dumps(payload, indent=2, ensure_ascii=False))
                    print("=" * 80)
                    
                    # Make the HTTP request to the AI provider
                    import requests
                    response = requests.post(
                        api_endpoint,
                        json=payload,
                        headers=headers,
                        timeout=30.0  # 30 second timeout
                    )
                    
                    print(f"响应状态码: {response.status_code}")

                    if response.status_code == 200:
                        response_data = response.json()
                        ai_reply_content = response_data['choices'][0]['message']['content']
                        print("响应内容:")
                        print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    elif response.status_code == 401:
                        ai_reply_content = f"API密钥无效或已过期。错误代码: {response.status_code}"
                        print(f"错误详情: {response.text}")
                    elif response.status_code == 404:
                        ai_reply_content = f"API端点未找到。请检查API URL是否正确。错误代码: {response.status_code}"
                        print(f"错误详情: {response.text}")
                    elif response.status_code == 429:
                        ai_reply_content = f"API请求频率超限。错误代码: {response.status_code}"
                        print(f"错误详情: {response.text}")
                    else:
                        error_detail = response.text
                        ai_reply_content = f"AI服务调用失败。状态码: {response.status_code}, 详情: {error_detail}"
                        print(f"错误详情: {response.text}")

                    print("=" * 80)
                        
            except Exception as e:
                import traceback
                traceback.print_exc() # Print full traceback to backend logs
                print(f"Debug: AI call failed - {type(e).__name__}: {str(e)}")
                ai_reply_content = f"AI服务调用失败: {type(e).__name__}: {str(e)}"
    else:
        ai_reply_content = f"AI服务未配置。请在AI管理中选择一个AI模型。"

    # ---------------------

    # 保存AI消息
    ai_message = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=ai_reply_content
    )
    db.add(ai_message)
    db.commit()

    return {"reply": ai_reply_content, "conversation_id": conversation_id}





# 启动服务器
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 9009))  # Allow port to be configured via environment variable
    print(f"正在启动 StoryForge API 服务器...")
    print(f"服务器将在 http://localhost:{port} 运行")
    uvicorn.run(app, host="0.0.0.0", port=port)
