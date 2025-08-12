"""
Integration tests for API endpoints
Tests actual HTTP responses and service integration
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os

# Import the FastAPI app
from app.main import app
from app.core.config import get_settings


@pytest.fixture
def test_env():
    """Setup test environment variables"""
    env_vars = {
        "DATABASE_URL": "sqlite:///test.db",
        "COMPANION_TOKEN": "test-token-1234567890123456789012",
        "SECRET_KEY": "test-secret-key-1234567890123456789012",
        "LLM_PROVIDER": "none",
        "DEBUG": "true"
    }
    
    with patch.dict(os.environ, env_vars):
        # Clear settings cache
        import app.core.config
        app.core.config.settings = None
        yield env_vars


@pytest.fixture
def client(test_env):
    """Create test client"""
    return TestClient(app)


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health endpoint returns success"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["app_name"] == "Apply-Copilot"
        assert data["llm_provider"] == "none"
        assert data["environment"] == "development"


@pytest.mark.integration 
class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns basic info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Apply-Copilot API"
        assert "version" in data
        assert data["docs"] == "/docs"  # Debug mode enabled


@pytest.mark.integration
class TestLLMTestEndpoint:
    """Test LLM test endpoint (debug only)"""
    
    def test_llm_test_endpoint_debug_mode(self, client):
        """Test LLM test endpoint works in debug mode"""
        response = client.post("/api/llm/test", json={
            "messages": [{"role": "user", "content": "test"}]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["provider"] == "none"
        assert data["status"] == "success"
        assert "response" in data
        assert "model_info" in data
    
    def test_llm_test_endpoint_production_mode(self, test_env):
        """Test LLM test endpoint disabled in production"""
        # Override DEBUG to false
        test_env["DEBUG"] = "false"
        
        with patch.dict(os.environ, test_env):
            import app.core.config
            app.core.config.settings = None
            
            client = TestClient(app)
            response = client.post("/api/llm/test", json={})
            
            assert response.status_code == 404


@pytest.mark.integration
class TestJTREndpoint:
    """Test Job-Tailored Resume endpoint"""
    
    def test_jtr_endpoint_rule_based(self, client):
        """Test JTR endpoint with rule-based provider"""
        request_data = {
            "job_title": "Data Scientist",
            "job_description": "Looking for ML expert",
            "resume_profile": {"name": "Test User"}
        }
        
        response = client.post("/api/jtr", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "request_id" in data
        assert "match_score" in data
        assert "status" in data
        assert data["llm_provider"] == "none"
        assert "analysis" in data
    
    def test_jtr_endpoint_with_llm_error(self, client):
        """Test JTR endpoint handles LLM errors gracefully"""
        with patch('app.services.llm_provider.generate_llm_response', side_effect=Exception("LLM Error")):
            response = client.post("/api/jtr", json={"test": "data"})
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "rule_based"
            assert "error" in data
            assert "LLM Error" in data["error"]


@pytest.mark.integration
class TestActionPlanEndpoint:
    """Test action plan endpoint"""
    
    def test_action_plan_endpoint(self, client):
        """Test action plan endpoint basic functionality"""
        response = client.post("/api/plan", json={
            "fields": ["name", "email"],
            "page_context": "greenhouse"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "action_plan" in data
        assert "estimated_duration" in data


@pytest.mark.integration
class TestSubmitGuardEndpoint:
    """Test submit guard endpoint"""
    
    def test_submit_guard_endpoint(self, client):
        """Test submit guard endpoint basic functionality"""
        response = client.post("/api/submit-guard", json={
            "form_data": {"name": "Test"},
            "context": "test"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "validation_passed" in data
        assert "snapshot_id" in data


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error_handler(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_422_validation_error(self, client):
        """Test validation error handling"""
        # Send invalid JSON
        response = client.post("/api/jtr", json="invalid")
        
        # Should get validation error for non-dict input
        assert response.status_code in [422, 500]  # Depends on FastAPI version


@pytest.mark.integration 
@pytest.mark.slow
class TestAsyncEndpoints:
    """Test async endpoint functionality"""
    
    @pytest.mark.asyncio
    async def test_async_client_health(self, test_env):
        """Test async client with health endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_async_client_jtr(self, test_env):
        """Test async client with JTR endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/jtr", json={"test": "data"})
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data


@pytest.mark.integration
class TestCORSHeaders:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are present"""
        response = client.options("/health")
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers.keys()
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight request"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = client.options("/api/jtr", headers=headers)
        
        # Should allow the request
        assert response.status_code == 200