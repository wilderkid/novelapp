from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_get_projects():
    """测试获取项目列表接口"""
    response = client.get("/api/projects")
    assert response.status_code == 200
    # 验证返回的是一个JSON数组（列表）
    assert isinstance(response.json(), list)