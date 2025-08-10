import os
import pytest
import tempfile
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import Config


class TestConfig:
    def test_from_yaml_basic(self):
        """Test loading basic YAML config"""
        yaml_content = """
api_name: "Test API"
base_url: "https://test.com"
timeout: 30
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            config = Config.from_yaml(f.name)
            assert config.get('api_name') == "Test API"
            assert config.get('base_url') == "https://test.com"
            assert config.get('timeout') == 30
            
            os.unlink(f.name)
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution in config"""
        os.environ['TEST_API_KEY'] = 'secret123'
        os.environ['TEST_URL'] = 'https://example.com'
        
        yaml_content = """
api_key: "${TEST_API_KEY}"
base_url: "${TEST_URL}"
default_value: "${MISSING_VAR:default}"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            config = Config.from_yaml(f.name)
            assert config.get('api_key') == 'secret123'
            assert config.get('base_url') == 'https://example.com'
            assert config.get('default_value') == 'default'
            
            os.unlink(f.name)
            del os.environ['TEST_API_KEY']
            del os.environ['TEST_URL']
    
    def test_nested_config_access(self):
        """Test accessing nested configuration values"""
        yaml_content = """
logging:
  level: "DEBUG"
  format: "%(message)s"
api:
  endpoints:
    analyze: "/v1/analyze"
    status: "/v1/status"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            config = Config.from_yaml(f.name)
            assert config.get('logging.level') == "DEBUG"
            assert config.get('api.endpoints.analyze') == "/v1/analyze"
            assert config.get('missing.key', 'default') == 'default'
            
            os.unlink(f.name)
    
    def test_to_dict(self):
        """Test converting config to dictionary"""
        yaml_content = """
key1: "value1"
key2: 123
key3:
  nested: "value"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            config = Config.from_yaml(f.name)
            data = config.to_dict()
            assert isinstance(data, dict)
            assert data['key1'] == "value1"
            assert data['key2'] == 123
            assert data['key3']['nested'] == "value"
            
            os.unlink(f.name)
    
    def test_invalid_yaml(self):
        """Test handling of invalid YAML"""
        yaml_content = """
invalid: yaml: content
- no proper structure
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            with pytest.raises(Exception):
                Config.from_yaml(f.name)
            
            os.unlink(f.name)
    
    def test_missing_file(self):
        """Test handling of missing config file"""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml('/nonexistent/path/config.yaml')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])