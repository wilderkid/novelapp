import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base
from models import Project, AIProvider, AIModel

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_read_main():
    """测试根路径是否可访问"""
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_project():
    """测试创建项目"""
    project_data = {
        "title": "测试项目",
        "description": "这是一个测试项目",
        "author": "测试作者",
        "genre": "科幻"
    }
    response = client.post("/api/projects", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试项目"
    assert data["author"] == "测试作者"

def test_get_projects():
    """测试获取项目列表"""
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)

def test_create_ai_provider():
    """测试创建AI提供商"""
    provider_data = {
        "name": "测试提供商",
        "base_url": "https://api.test.com",
        "api_key": "test-key",
        "enabled": True
    }
    response = client.post("/api/ai-providers", json=provider_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试提供商"
    assert data["enabled"] == True

def test_get_ai_providers():
    """测试获取AI提供商列表"""
    response = client.get("/api/ai-providers")
    assert response.status_code == 200
    providers = response.json()
    assert isinstance(providers, list)

def test_get_prompt_templates():
    """测试获取提示模板列表"""
    response = client.get("/api/prompt-templates")
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)

def test_get_novel_genres():
    """测试获取小说类型列表"""
    response = client.get("/api/novel-genres")
    assert response.status_code == 200
    genres = response.json()
    assert isinstance(genres, list)

def test_health_check():
    """测试API健康检查"""
    # 测试多个基础端点确保API正常工作
    endpoints = [
        "/api/projects",
        "/api/ai-providers", 
        "/api/prompt-templates",
        "/api/novel-genres"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"端点 {endpoint} 返回状态码 {response.status_code}"

if __name__ == "__main__":
    pytest.main([__file__])