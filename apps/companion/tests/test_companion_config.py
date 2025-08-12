"""
Unit tests for companion service configuration
Tests Golden Rules compliance and security validation
"""

import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError

from main import CompanionSettings, mask_token


class TestMaskToken:
    """Test token masking functionality"""
    
    def test_mask_token_standard(self):
        """Test masking of standard token"""
        token = "abcdefghijklmnopqrstuvwxyz123456"
        result = mask_token(token)
        assert result == "abcdefgh***"
        assert "ijklmnopqrstuvwxyz123456" not in result
    
    def test_mask_token_short(self):
        """Test masking of short token"""
        token = "short"
        result = mask_token(token)
        assert result == "***"
    
    def test_mask_token_empty(self):
        """Test masking of empty token"""
        assert mask_token("") == "***"
        assert mask_token(None) == "***"


class TestCompanionSettingsValidation:
    """Test companion settings validation"""
    
    def test_host_validation_localhost_allowed(self):
        """Test localhost host is allowed"""
        with patch.dict(os.environ, {
            "COMPANION_HOST": "127.0.0.1",
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = CompanionSettings()
            assert settings.host == "127.0.0.1"
    
    def test_host_validation_localhost_name_allowed(self):
        """Test localhost name is allowed"""
        with patch.dict(os.environ, {
            "COMPANION_HOST": "localhost",
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = CompanionSettings()
            assert settings.host == "localhost"
    
    def test_host_validation_remote_forbidden(self):
        """Test remote host is forbidden (CRITICAL SECURITY)"""
        with patch.dict(os.environ, {
            "COMPANION_HOST": "0.0.0.0",
            "COMPANION_TOKEN": "a" * 32
        }):
            with pytest.raises(ValidationError, match="Companion service MUST run on localhost only"):
                CompanionSettings()
    
    def test_host_validation_external_ip_forbidden(self):
        """Test external IP is forbidden (CRITICAL SECURITY)"""
        with patch.dict(os.environ, {
            "COMPANION_HOST": "192.168.1.100",
            "COMPANION_TOKEN": "a" * 32
        }):
            with pytest.raises(ValidationError, match="Companion service MUST run on localhost only"):
                CompanionSettings()
    
    def test_auth_token_validation_too_short(self):
        """Test auth token validation fails for short tokens"""
        with patch.dict(os.environ, {
            "COMPANION_TOKEN": "short"
        }):
            with pytest.raises(ValidationError, match="COMPANION_TOKEN must be at least 32 characters"):
                CompanionSettings()
    
    def test_auth_token_validation_valid(self):
        """Test auth token validation passes for long tokens"""
        token = "a" * 32
        with patch.dict(os.environ, {
            "COMPANION_TOKEN": token
        }):
            settings = CompanionSettings()
            assert settings.auth_token == token
    
    def test_safe_logging_masks_token(self):
        """Test safe logging masks the auth token"""
        token = "supersecrettoken123456789012345"
        
        with patch.dict(os.environ, {
            "COMPANION_TOKEN": token
        }):
            settings = CompanionSettings()
            
            # Mock the logger to capture log calls
            with patch('main.logger') as mock_logger:
                settings.log_startup_config()
                
                # Verify logger was called
                assert mock_logger.info.called
                
                # Get the logged data
                call_args = mock_logger.info.call_args
                logged_data = call_args[1]  # kwargs
                
                # Verify token is masked
                assert "supersecrettoken123456789012345" not in str(logged_data)
                assert "***" in str(logged_data)


class TestCompanionSecurityFeatures:
    """Test companion service security features"""
    
    def test_default_host_is_localhost(self):
        """Test default host is localhost for security"""
        with patch.dict(os.environ, {
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = CompanionSettings()
            assert settings.host == "127.0.0.1"
    
    def test_default_port_is_8765(self):
        """Test default port is 8765"""
        with patch.dict(os.environ, {
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = CompanionSettings()
            assert settings.port == 8765
    
    def test_security_features_enabled_by_default(self):
        """Test security features are enabled by default"""
        with patch.dict(os.environ, {
            "COMPANION_TOKEN": "a" * 32
        }):
            settings = CompanionSettings()
            assert settings.enable_ocr == True
            assert settings.enable_screenshots == True
            assert settings.coordinate_tolerance == 3
            assert settings.max_click_distance == 50


class TestCompanionEnvironmentIntegration:
    """Test companion environment integration"""
    
    def test_environment_variables_loaded(self):
        """Test environment variables are properly loaded"""
        env_vars = {
            "COMPANION_HOST": "127.0.0.1",
            "COMPANION_PORT": "9999",
            "COMPANION_TOKEN": "test-token-1234567890123456789012",
            "ENABLE_OCR": "false",
            "COORDINATE_TOLERANCE": "5",
            "DEBUG": "true"
        }
        
        with patch.dict(os.environ, env_vars):
            settings = CompanionSettings()
            
            assert settings.host == "127.0.0.1"
            assert settings.port == 9999
            assert settings.auth_token == "test-token-1234567890123456789012"
            assert settings.enable_ocr == False
            assert settings.coordinate_tolerance == 5
            assert settings.debug == True