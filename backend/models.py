from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float, JSON
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    description = Column(Text)
    author = Column(String)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系

    volumes = relationship("Volume", back_populates="project")
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    # 移除与Conversation的关系，使AI对话功能不依赖项目
    worldviews = relationship("Worldview", back_populates="project")
    rpg_characters = relationship("RPGCharacter", back_populates="project")
    organizations = relationship("Organization", back_populates="project")
    supernatural_powers = relationship("SupernaturalPower", back_populates="project")
    weapons = relationship("Weapon", back_populates="project")
    dungeons = relationship("Dungeon", back_populates="project")
    prompt_templates = relationship("PromptTemplate", back_populates="project")  # 添加与项目的关系



class Volume(Base):
    __tablename__ = "volumes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    project = relationship("Project", back_populates="volumes")
    chapters = relationship("Chapter", back_populates="volume")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    volume_id = Column(Integer, ForeignKey("volumes.id"))
    title = Column(String, nullable=False)
    content = Column(Text)
    word_count = Column(Integer, default=0)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    project = relationship("Project", back_populates="chapters")
    volume = relationship("Volume", back_populates="chapters")


class AIProvider(Base):
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 例如: "OpenAI", "Gemini"
    api_key = Column(String)
    base_url = Column(String)
    enabled = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    models = relationship("AIModel", back_populates="provider", cascade="all, delete-orphan")

class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    name = Column(String, nullable=False) # 用户友好的名称, 例如: "Creative Writing (GPT-4)"
    model_identifier = Column(String, nullable=False) # 模型的实际ID, 例如: "gpt-4-1106-preview"
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    is_default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    provider = relationship("AIProvider", back_populates="models")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    content = Column(Text, nullable=False)
    variables = Column(JSON)
    is_default = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"))  # 添加项目ID字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="prompt_templates")  # 添加与项目的关系


class Worldview(Base):
    __tablename__ = "worldviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="worldviews")

class RPGCharacter(Base):
    __tablename__ = "rpg_characters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    content = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="rpg_characters")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    content = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="organizations")

class SupernaturalPower(Base):
    __tablename__ = "supernatural_powers"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    content = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="supernatural_powers")

class Weapon(Base):
    __tablename__ = "weapons"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    content = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="weapons")

class Dungeon(Base):
    __tablename__ = 'dungeons'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String, nullable=False)
    content = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    project = relationship("Project", back_populates="dungeons")


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    # 移除project_id，使AI对话功能不依赖项目
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 移除与Project的关系，使AI对话功能不依赖项目
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class NovelGenre(Base):
    __tablename__ = "novel_genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())