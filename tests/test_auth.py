"""
认证接口测试
"""
import pytest
from httpx import AsyncClient


class TestAuth:
    """认证测试类"""

    @pytest.mark.asyncio
    async def test_login(self, client: AsyncClient):
        """测试登录接口"""
        response = await client.post(
            "/admin-api/system/auth/login",
            json={
                "username": "admin",
                "password": "123456",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient):
        """测试错误密码登录"""
        response = await client.post(
            "/admin-api/system/auth/login",
            json={
                "username": "admin",
                "password": "wrong_password",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"