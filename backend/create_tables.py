
#!/usr/bin/env python3
"""
创建数据库表脚本 - 使用SQLAlchemy自动创建表
"""
from database import engine, Base
from models import Project, Volume, Chapter, AIProvider, AIModel, PromptTemplate, Worldview, RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon, Conversation, Message
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_tables():
    """创建所有数据库表"""
    try:
        print("开始创建数据库表...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建完成！")
        
        # 创建会话并插入默认数据
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            # 检查是否已存在系统AI提供商
            existing_providers = db.query(AIProvider).filter(AIProvider.is_system == True).all()
            if not existing_providers:
                print("插入默认系统AI提供商...")
                # 插入默认的系统AI提供商
                system_providers = [
                    AIProvider(name="OpenAI", api_key="", base_url="https://api.openai.com/v1", enabled=True, is_system=True),
                    AIProvider(name="Gemini", api_key="", base_url="https://generativelanguage.googleapis.com", enabled=True, is_system=True),
                    AIProvider(name="Claude", api_key="", base_url="https://api.anthropic.com", enabled=True, is_system=True),
                ]
                
                for provider in system_providers:
                    db.add(provider)
                db.commit()
                
                # 为每个提供商添加默认模型
                providers = db.query(AIProvider).filter(AIProvider.is_system == True).all()
                models = [
                    AIModel(provider_id=providers[0].id, name="GPT-3.5 Turbo", model_identifier="gpt-3.5-turbo", temperature=0.7, max_tokens=2000, is_default=True, enabled=True),
                    AIModel(provider_id=providers[0].id, name="GPT-4", model_identifier="gpt-4", temperature=0.7, max_tokens=4000, is_default=False, enabled=True),
                    AIModel(provider_id=providers[1].id, name="Gemini Pro", model_identifier="gemini-pro", temperature=0.7, max_tokens=2000, is_default=True, enabled=True),
                    AIModel(provider_id=providers[2].id, name="Claude 3 Haiku", model_identifier="claude-3-haiku-20240307", temperature=0.7, max_tokens=2000, is_default=True, enabled=True),
                ]
                
                for model in models:
                    db.add(model)
                db.commit()
                print("默认系统AI提供商和模型插入完成")
            
            # 检查是否已存在默认提示词模板
            existing_templates = db.query(PromptTemplate).filter(PromptTemplate.is_default == True).all()
            if not existing_templates:
                print("插入默认提示词模板...")
                # 插入默认的提示词模板（全局级别，不关联项目）
                templates = [
                    PromptTemplate(
                        name="小说创作助手",
                        category="创作",
                        content="请你扮演一位专业的小说创作助手，帮助作者进行小说创作。请根据以下要求提供创作建议和内容：\n\n{{content}}\n\n请确保内容符合小说的逻辑性和文学性。",
                        is_default=True
                    ),
                    PromptTemplate(
                        name="角色设定",
                        category="角色",
                        content="请帮我完善这个角色设定：\n\n角色名称：{{character_name}}\n基本背景：{{background}}\n\n请提供详细的角色性格、动机、成长轨迹等信息。",
                        is_default=True
                    ),
                    PromptTemplate(
                        name="世界观构建",
                        category="世界观",
                        content="请帮我构建这个奇幻世界的设定：\n\n世界名称：{{world_name}}\n基本特征：{{features}}\n\n请详细描述这个世界的地理、历史、文化、魔法体系等。",
                        is_default=True
                    ),
                    PromptTemplate(
                        name="情节发展",
                        category="情节",
                        content="请帮我设计接下来的情节发展：\n\n当前情节：{{current_plot}}\n期望方向：{{direction}}\n\n请提供具体的情节建议和冲突设置。",
                        is_default=True
                    ),
                ]
                
                for template in templates:
                    db.add(template)
                db.commit()
                print("默认提示词模板插入完成")
            
        finally:
            db.close()
        
        print("所有数据库初始化完成！")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()