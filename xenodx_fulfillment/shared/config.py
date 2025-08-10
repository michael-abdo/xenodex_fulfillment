"""Shared configuration management for all API integrations"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager with environment variable support"""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize with configuration data"""
        self._data = data
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """
        Load configuration from YAML file with env var substitution
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            Config instance
        """
        with open(yaml_path, 'r') as f:
            content = f.read()
        
        # Substitute environment variables
        content = cls._substitute_env_vars(content)
        
        # Parse YAML
        data = yaml.safe_load(content)
        
        return cls(data)
    
    @staticmethod
    def _substitute_env_vars(content: str) -> str:
        """
        Replace ${VAR_NAME} with environment variable values
        
        Args:
            content: YAML content string
            
        Returns:
            Content with env vars substituted
        """
        import re
        
        def replace_var(match):
            var_expr = match.group(1)
            
            # Handle ${VAR:default} syntax
            if ':' in var_expr:
                var_name, default = var_expr.split(':', 1)
            else:
                var_name = var_expr
                default = ''
            
            return os.environ.get(var_name, default)
        
        # Replace ${VAR} patterns
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_var, content)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key
        
        Args:
            key: Configuration key (e.g., 'api.base_url')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary"""
        return self._data.copy()