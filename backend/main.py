
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
from pydantic import BaseModel, Field

from database import SessionLocal, engine, Base
from sqlalchemy import func
from models import (
    Project, Volume, Chapter,
    AIProvider, AIModel, PromptTemplate,
    Worldview, RPGCharacter, Organization,
    SupernaturalPower, Weapon, Dungeon,
    Conversation, Message, NovelGenre
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
    ConversationResponse, MessageResponse, ConversationUpdate,
    NovelGenreCreate, NovelGenreResponse
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# FastAPI应用
app = FastAPI(title="StoryForge API", version="1.0.0")

# CORS配置 - 允许局域网访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问
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

# URL处理函数 - 与前端保持一致
def process_openai_url(base_url: str) -> str:
    """
    处理OpenAI兼容API的URL，与前端逻辑保持一致
    规则1: URL以#结尾，移除#后直接使用
    规则2: URL以/结尾，移除/后补充 /chat/completions
    规则3: URL不以/结尾，补充 /v1/chat/completions
    """
    base_url = base_url.strip()
    
    # 规则1: 以#结尾，移除#后直接使用
    if base_url.endswith('#'):
        return base_url[:-1]
    
    # 规则2: 以/结尾，移除/后补充 /chat/completions
    if base_url.endswith('/'):
        return f"{base_url[:-1]}/chat/completions"
    
    # 规则3: 不以/结尾，补充 /v1/chat/completions
    return f"{base_url}/v1/chat/completions"


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



class ChapterImport(BaseModel):
    title: str
    content: str
    order: int

class VolumeImport(BaseModel):
    title: str
    order: int
    chapters: List[ChapterImport]

class NovelImport(BaseModel):
    title: str
    genre: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    volumes: List[VolumeImport]

@app.post("/api/projects/import", response_model=ProjectResponse)
def import_project(novel_data: NovelImport, db: Session = Depends(get_db)):
    """导入新项目"""
    print("Importing novel data:", novel_data.model_dump_json(indent=2))
    # 创建项目
    db_project = Project(
        title=novel_data.title,
        genre=novel_data.genre,
        description=novel_data.description,
        author=novel_data.author
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 导入分卷和章节
    for volume_data in novel_data.volumes:
        db_volume = Volume(
            title=volume_data.title,
            project_id=db_project.id,
            order=volume_data.order
        )
        db.add(db_volume)
        db.commit()
        db.refresh(db_volume)

        for chapter_data in volume_data.chapters:
            db_chapter = Chapter(
                title=chapter_data.title,
                content=chapter_data.content,
                volume_id=db_volume.id,
                project_id=db_project.id,
                order=chapter_data.order,
                word_count=len(chapter_data.content)
            )
            db.add(db_chapter)
            db.commit()
            db.refresh(db_chapter)

    return db_project

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

# AI 提供商相关 API
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

# 获取所有AI模型（包括其提供商信息）
@app.get("/api/ai-models", response_model=List[AIModelResponse])
def get_all_ai_models(db: Session = Depends(get_db)):
    """获取所有AI模型（包括其提供商信息）"""
    models = (
        db.query(AIModel)
        .join(AIProvider)
        .filter(AIModel.enabled == True, AIProvider.enabled == True)
        .options(joinedload(AIModel.provider))
        .all()
    )
    return models


# 提示模板相关API
@app.get("/api/prompt-templates", response_model=List[PromptTemplateResponse])
def get_prompt_templates(db: Session = Depends(get_db)):
    """获取所有提示模板"""
    try:
        templates = db.query(PromptTemplate).all()
        return templates
    except Exception as e:
        print(f"查询提示词模板时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.post("/api/prompt-templates", response_model=PromptTemplateResponse)
def create_prompt_template(template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """创建新的提示模板"""
    db_template = PromptTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@app.get("/api/projects/{project_id}/prompt-templates", response_model=List[PromptTemplateResponse])
def get_project_prompt_templates(project_id: int, db: Session = Depends(get_db)):
    """获取项目的所有提示模板（返回所有全局提示词模板）"""
    templates = db.query(PromptTemplate).all()
    return templates

@app.put("/api/prompt-templates/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(template_id: int, template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """更新提示模板"""
    db_template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="提示模板不存在")

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

    if not project_id or '{{' not in content:
        return {"rendered_content": content}

    search_models = [
        Worldview, RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon, Chapter, Volume, Project
    ]

    def replacer(match):
        keyword = match.group(1).strip()
        
        # 特殊处理世界观：使用固定关键词"世界观"
        if keyword == "世界观":
            worldview = db.query(Worldview).filter(Worldview.project_id == project_id).first()
            if worldview and worldview.content:
                return str(worldview.content)
        
        for model in search_models:
            # 跳过Worldview，因为已经特殊处理
            if model == Worldview:
                continue
                
            query = db.query(model)
            query_attr = 'name' if hasattr(model, 'name') else 'title'

            if model == Chapter:
                query = query.filter(Chapter.project_id == project_id, Chapter.title.startswith(keyword))
            elif hasattr(model, 'project_id'):
                query = query.filter(model.project_id == project_id, getattr(model, query_attr) == keyword)
            else:
                query = query.filter(getattr(model, query_attr) == keyword)

            result = query.first()
            
            if result:
                found_content = None
                if hasattr(result, 'content') and result.content:
                    found_content = result.content
                elif hasattr(result, 'description') and result.description:
                    found_content = result.description
                else:
                    found_content = getattr(result, query_attr, '')
                return str(found_content)

        return match.group(0) # Return original if no match found

    final_content = re.sub(r'\{\{\s*(.*?)\s*\}\}', replacer, content)
    return {"rendered_content": final_content}


class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None # 新增：允许前端传递项目ID
    conversation_id: Optional[int] = None
    history: List[dict] = []
    prompt_template_id: Optional[int] = None
    ai_model_id: Optional[int] = None
    resources: Optional[dict] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    selected_text: Optional[str] = None # 新增：编辑器中选中的文字

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
            system_prompt = process_prompt_template(db, prompt_template, request.project_id, request.resources, request.selected_text)

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
                base_url = selected_ai_provider.base_url or "https://api.openai.com"
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
                        "temperature": request.temperature if request.temperature is not None else selected_ai_model.temperature,
                        "max_tokens": request.max_tokens if request.max_tokens is not None else selected_ai_model.max_tokens,
                    }

                    # Check if this is a thinking model and add enable_thinking parameter
                    is_thinking_model = "thinking" in selected_ai_model.model_identifier.lower() or "qwen" in selected_ai_model.model_identifier.lower()
                    if is_thinking_model:
                        payload["extra_body"] = {"enable_thinking": True}

                    # 使用与前端一致的URL处理逻辑
                    api_endpoint = process_openai_url(base_url)

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
            system_prompt = process_prompt_template(db, prompt_template, request.project_id, request.resources, request.selected_text)

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
        base_url = selected_ai_provider.base_url or "https://api.openai.com"
        api_key = selected_ai_provider.api_key
        # 使用与前端一致的URL处理逻辑
        api_endpoint = process_openai_url(base_url)
        
        print(f"[API请求] 完整的API端点: {api_endpoint}")
        print(f"[API请求] 基础URL: {base_url}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 准备请求载荷，启用流式响应
        payload = {
            "model": selected_ai_model.model_identifier,
            "messages": messages_for_ai,
            "temperature": request.temperature if request.temperature is not None else selected_ai_model.temperature,
            "max_tokens": request.max_tokens if request.max_tokens is not None else selected_ai_model.max_tokens,
            "stream": True  # 启用流式响应
        }

        # Check if this is a thinking model and add enable_thinking parameter
        is_thinking_model = "thinking" in selected_ai_model.model_identifier.lower() or "qwen" in selected_ai_model.model_identifier.lower()
        if is_thinking_model:
            payload["extra_body"] = {"enable_thinking": True}

        # 使用httpx进行异步请求，支持流式响应
        import httpx
        import os

        try:
            print(f"[HTTP请求] 准备发送请求到: {api_endpoint}")
            print(f"[HTTP请求] 请求头: {headers}")
            print(f"[HTTP请求] 请求体: {json.dumps(payload, ensure_ascii=False)[:500]}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    api_endpoint,
                    json=payload,
                    headers=headers
                ) as response:
                    print(f"[HTTP响应] 状态码: {response.status_code}")
                    print(f"[HTTP响应] 响应头: {dict(response.headers)}")
                    
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

                    # --- AI响应适配器 ---
                    class AIResponseAdapter:
                        def parse(self, delta):
                            raise NotImplementedError

                    class DefaultAdapter(AIResponseAdapter):
                        def parse(self, delta):
                            thinking_chunk = delta.get("reasoning_content")
                            content_chunk = delta.get("content")
                            return thinking_chunk, content_chunk

                    class ReasoningAdapter(AIResponseAdapter):
                        def parse(self, delta):
                            thinking_chunk = delta.get("reasoning")
                            content_chunk = delta.get("content")
                            return thinking_chunk, content_chunk

                    def get_adapter(model_name, sample_delta):
                        # 优先基于样本内容判断
                        if "reasoning" in sample_delta:
                            print("[适配器] 检测到 'reasoning' 字段，使用 ReasoningAdapter")
                            return ReasoningAdapter()
                        if "reasoning_content" in sample_delta:
                            print("[适配器] 检测到 'reasoning_content' 字段，使用 DefaultAdapter")
                            return DefaultAdapter()
                        
                        # 如果样本中没有特定字段，则基于模型名称判断（作为备用方案）
                        if "glm" in model_name.lower() or "zhipu" in model_name.lower():
                            print(f"[适配器] 模型名称 '{model_name}' 包含 'glm' 或 'zhipu'，使用 ReasoningAdapter")
                            return ReasoningAdapter()
                        
                        print(f"[适配器] 未匹配到特定适配器，使用 DefaultAdapter")
                        return DefaultAdapter()

                    # --- 流式处理 ---
                    adapter = None
                    line_count = 0
                    async for line in response.aiter_lines():
                        if line:
                            line_count += 1
                            print(f"[流式响应 #{line_count}] 原始行: {line[:200]}")

                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str.strip() == "[DONE]":
                                    print("[流式响应] 收到结束标记 [DONE]")
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    print(f"[流式响应] 解析的JSON: {json.dumps(data, ensure_ascii=False)[:300]}")

                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("delta", {})
                                        print(f"[流式响应] Delta内容: {delta}")

                                        # 在第一次收到delta时，动态选择适配器
                                        if adapter is None:
                                            adapter = get_adapter(selected_ai_model.model_identifier, delta)

                                        thinking_chunk, content_chunk = adapter.parse(delta)

                                        # 统一处理思考过程
                                        if thinking_chunk:
                                            print(f"[流式响应] 发送思考内容: {thinking_chunk[:100]}")
                                            yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_chunk})}\n\n"
                                        
                                        # 统一处理最终回复
                                        if content_chunk:
                                            print(f"[流式响应] 发送回复内容: {content_chunk}")
                                            ai_reply_content += content_chunk
                                            yield f"data: {json.dumps({'type': 'content', 'content': content_chunk})}\n\n"
                                        
                                except json.JSONDecodeError as e:
                                    print(f"[流式响应] JSON解析失败: {e}, 原始数据: {data_str[:200]}")
                                    pass
                    
                    print(f"[流式响应] 总共收到 {line_count} 行，最终回复内容长度: {len(ai_reply_content)}")

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

# 小说类型管理API
@app.get("/api/novel-genres", response_model=List[NovelGenreResponse])
def get_novel_genres(db: Session = Depends(get_db)):
    """获取所有小说类型"""
    genres = db.query(NovelGenre).all()
    return genres

@app.post("/api/novel-genres", response_model=NovelGenreResponse)
def create_novel_genre(genre: NovelGenreCreate, db: Session = Depends(get_db)):
    """创建新的小说类型"""
    db_genre = NovelGenre(**genre.model_dump())
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

@app.put("/api/novel-genres/{genre_id}", response_model=NovelGenreResponse)
def update_novel_genre(genre_id: int, genre: NovelGenreCreate, db: Session = Depends(get_db)):
    """更新小说类型"""
    db_genre = db.query(NovelGenre).filter(NovelGenre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=404, detail="小说类型不存在")
    
    db_genre.name = genre.name
    db.commit()
    db.refresh(db_genre)
    return db_genre

@app.delete("/api/novel-genres/{genre_id}")
def delete_novel_genre(genre_id: int, db: Session = Depends(get_db)):
    """删除小说类型"""
    db_genre = db.query(NovelGenre).filter(NovelGenre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=404, detail="小说类型不存在")
    
    db.delete(db_genre)
    db.commit()
    return {"message": "小说类型已删除"}

# 启动服务器
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 9009))  # Allow port to be configured via environment variable
    print(f"正在启动 StoryForge API 服务器...")
    print(f"服务器将在 http://localhost:{port} 运行")
    uvicorn.run(app, host="0.0.0.0", port=port)
