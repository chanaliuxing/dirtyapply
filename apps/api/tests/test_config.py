"""
Unit tests for configuration module
Tests Golden Rules compliance and fail-fast validation
"""

import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError

from app.core.config import Settings, get_settings, validate_environment, mask_secret


class TestMaskSecret:
    """Test secret masking functionality"""
    
    def test_mask_secret_standard_api_key(self):
        """Test masking of standard API key"""
        secret = "sk-1234567890abcdef"
        result = mask_secret(secret)
        assert result == "sk-12345***"
        assert "1234567890abcdef" not in result
    
    def test_mask_secret_nvidia_key(self):
        """Test masking of NVIDIA API key"""
        secret = "nvapi-ZwdrWQivT52mdpS4EeSu"
        result = mask_secret(secret)
        assert result == "nvapi-Zw***"
        assert "ZwdrWQivT52mdpS4EeSu" not in result
    
    def test_mask_secret_short_key(self):
        """Test masking of short secrets"""
        secret = "short"
        result = mask_secret(secret)
        assert result == "***"
    
    def test_mask_secret_empty(self):
        """Test masking of empty/None secrets"""
        assert mask_secret("") == "***"
        assert mask_secret(None) == "***"


class TestSettingsValidation:
    """Test settings validation and Golden Rules compliance"""
    
    def test_openai_api_key_validation_valid(self):
        """Test valid OpenAI API key passes validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "OPENAI_API_KEY": "sk-1234567890abcdef"
        }):
            settings = Settings()
            assert settings.openai_api_key == "sk-1234567890abcdef"
    
    def test_openai_api_key_validation_invalid(self):
        """Test invalid OpenAI API key fails validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db", 
            "COMPANION_TOKEN": "a" * 32,
            "OPENAI_API_KEY": "invalid-key"
        }):
            with pytest.raises(ValidationError, match="Invalid OpenAI API key format"):
                Settings()
    
    def test_nvidia_api_key_validation_valid(self):
        """Test valid NVIDIA API key passes validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "DEEPSEEK_NVIDIA_API_KEY": "nvapi-1234567890abcdef"
        }):
            settings = Settings()
            assert settings.deepseek_nvidia_api_key == "nvapi-1234567890abcdef"
    
    def test_nvidia_api_key_validation_invalid(self):
        """Test invalid NVIDIA API key fails validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "DEEPSEEK_NVIDIA_API_KEY": "invalid-nvidia-key"
        }):
            with pytest.raises(ValidationError, match="Invalid DeepSeek NVIDIA API key format"):
                Settings()
    
    def test_companion_token_validation_too_short(self):
        """Test companion token validation fails for short tokens"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "short"
        }):
            with pytest.raises(ValidationError, match="COMPANION_TOKEN must be at least 32 characters"):
                Settings()
    
    def test_companion_token_validation_valid(self):
        """Test companion token validation passes for long tokens"""
        token = "a" * 32
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": token
        }):
            settings = Settings()
            assert settings.companion_token == token
    
    def test_database_url_validation_postgresql(self):
        """Test PostgreSQL database URL validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = Settings()
            assert "postgresql://" in settings.database_url
    
    def test_database_url_validation_sqlite(self):
        """Test SQLite database URL validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = Settings()
            assert "sqlite:///" in settings.database_url
    
    def test_database_url_validation_invalid(self):
        """Test invalid database URL fails validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "mysql://invalid",
            "COMPANION_TOKEN": "a" * 32
        }):
            with pytest.raises(ValidationError, match="DATABASE_URL must be a valid PostgreSQL or SQLite URL"):
                Settings()


class TestLLMDependencyValidation:
    """Test LLM provider dependency validation"""
    
    def test_llm_provider_none_no_keys_required(self):
        """Test rule-based provider requires no API keys"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "LLM_PROVIDER": "none"
        }):
            settings = Settings()
            settings.validate_llm_dependencies()  # Should not raise
    
    def test_llm_provider_openai_requires_key(self):
        """Test OpenAI provider requires API key"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "LLM_PROVIDER": "openai"
        }):
            settings = Settings()
            with pytest.raises(ValueError, match="OPENAI_API_KEY is required when LLM_PROVIDER=openai"):
                settings.validate_llm_dependencies()
    
    def test_llm_provider_deepseek_nvidia_requires_key(self):
        """Test DeepSeek NVIDIA provider requires API key"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "LLM_PROVIDER": "deepseek-nvidia"
        }):
            settings = Settings()
            with pytest.raises(ValueError, match="DEEPSEEK_NVIDIA_API_KEY is required when LLM_PROVIDER=deepseek-nvidia"):
                settings.validate_llm_dependencies()
    
    def test_llm_provider_deepseek_nvidia_with_key_valid(self):
        """Test DeepSeek NVIDIA provider with valid key"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "LLM_PROVIDER": "deepseek-nvidia",
            "DEEPSEEK_NVIDIA_API_KEY": "nvapi-1234567890abcdef"
        }):
            settings = Settings()
            settings.validate_llm_dependencies()  # Should not raise


class TestProductionSecurityValidation:
    """Test production security validation"""
    
    def test_production_mode_disable_auth_forbidden(self):
        """Test production mode forbids DISABLE_AUTH=true"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "DEBUG": "false",
            "DISABLE_AUTH": "true"
        }):
            settings = Settings()
            with pytest.raises(ValueError, match="DISABLE_AUTH=true is not allowed in production"):
                settings.validate_production_security()
    
    def test_development_mode_allows_disable_auth(self):
        """Test development mode allows DISABLE_AUTH=true"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "DEBUG": "true",
            "DISABLE_AUTH": "true"
        }):
            settings = Settings()
            settings.validate_production_security()  # Should not raise


class TestEnvironmentValidation:
    """Test complete environment validation"""
    
    def test_validate_environment_success(self):
        """Test successful environment validation"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///test.db",
            "COMPANION_TOKEN": "a" * 32,
            "LLM_PROVIDER": "none"
        }):
            # Should not raise SystemExit
            validate_environment()
    
    def test_validate_environment_failure_exits(self):
        """Test failed environment validation causes SystemExit"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "invalid-url",
            "COMPANION_TOKEN": "short"
        }):
            with pytest.raises(SystemExit):
                validate_environment()


class TestSettingsLogging:
    """Test safe logging functionality"""
    
    def test_log_startup_config_masks_secrets(self):
        """Test startup logging masks sensitive information"""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:secret@localhost:5432/db",
            "COMPANION_TOKEN": "supersecrettoken123456789012345",
            "OPENAI_API_KEY": "sk-1234567890abcdef",
            "DEEPSEEK_NVIDIA_API_KEY": "nvapi-ZwdrWQivT52mdpS4EeSu"
        }):
            settings = Settings()
            
            # Mock the logger to capture log calls
            with patch('app.core.config.logger') as mock_logger:
                settings.log_startup_config()
                
                # Verify logger was called
                assert mock_logger.info.called
                
                # Get the logged data
                call_args = mock_logger.info.call_args
                logged_data = call_args[1]  # kwargs
                
                # Verify secrets are masked
                assert "secret" not in str(logged_data)
                assert "1234567890abcdef" not in str(logged_data)
                assert "ZwdrWQivT52mdpS4EeSu" not in str(logged_data)
                assert "***" in str(logged_data)