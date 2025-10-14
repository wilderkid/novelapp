
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
import uvicorn
import os
import json
import aiofiles
import httpx
from typing import List, Optional

from database import SessionLocal, engine, Base
from sqlalchemy import func
from models import Project, Volume, Chapter, AIConfig, PromptTemplate
from schemas import (
    ProjectCreate, ProjectResponse, 
    VolumeCreate, VolumeResponse,
    ChapterCreate, ChapterResponse,
    AIConfigCreate, AIConfigResponse,
    PromptTemplateCreate, PromptTemplateResponse
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(title="StoryForge API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# AI配置相关API
@app.get("/api/projects/{project_id}/ai-config", response_model=AIConfigResponse)
def get_ai_config(project_id: int, db: Session = Depends(get_db)):
    """获取项目的AI配置"""
    ai_config = db.query(AIConfig).filter(AIConfig.project_id == project_id).first()
    if not ai_config:
        # 如果没有配置，返回默认配置
        return AIConfigResponse(
            id=0,
            project_id=project_id,
            api_key="",
            model="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            max_tokens=2000,
            temperature=0.7
        )
    return ai_config

@app.post("/api/projects/{project_id}/ai-config", response_model=AIConfigResponse)
def create_ai_config(project_id: int, ai_config: AIConfigCreate, db: Session = Depends(get_db)):
    """创建AI配置"""
    # 先删除旧配置
    db.query(AIConfig).filter(AIConfig.project_id == project_id).delete()
    
    db_ai_config = AIConfig(project_id=project_id, **ai_config.dict())
    db.add(db_ai_config)
    db.commit()
    db.refresh(db_ai_config)
    return db_ai_config

@app.put("/api/projects/{project_id}/ai-config", response_model=AIConfigResponse)
def update_ai_config(project_id: int, ai_config: AIConfigCreate, db: Session = Depends(get_db)):
    """更新AI配置"""
    db_ai_config = db.query(AIConfig).filter(AIConfig.project_id == project_id).first()
    if not db_ai_config:
        raise HTTPException(status_code=404, detail="AI配置不存在")

    for key, value in ai_config.dict().items():
        setattr(db_ai_config, key, value)

    db.commit()
    db.refresh(db_ai_config)
    return db_ai_config

# 提示模板相关API
@app.get("/api/projects/{project_id}/prompt-templates", response_model=List[PromptTemplateResponse])
def get_prompt_templates(project_id: int, db: Session = Depends(get_db)):
    """获取项目的所有提示模板"""
    templates = db.query(PromptTemplate).filter(PromptTemplate.project_id == project_id).all()
    return templates

@app.post("/api/projects/{project_id}/prompt-templates", response_model=PromptTemplateResponse)
def create_prompt_template(project_id: int, template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """创建新的提示模板"""
    db_template = PromptTemplate(project_id=project_id, **template.dict())
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

    for key, value in template.dict().items():
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

# 启动服务器
if __name__ == "__main__":
    print("正在启动 StoryForge API 服务器...")
    print("服务器将在 http://localhost:9009 运行")
    uvicorn.run(app, host="0.0.0.0", port=9009)
