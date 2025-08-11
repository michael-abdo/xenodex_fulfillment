"""API Registry for managing available API integrations"""
from typing import Dict, List, Optional, Any


# Registry of available APIs and their implementation details
APIS: Dict[str, Dict[str, Any]] = {
    'behavior_signals': {
        'client_class': 'BehavioralSignalsClient',
        'analyzer_class': 'BehavioralSignalsAnalyzer',
        'import_path': 'xenodx_fulfillment.apis.behavior_signals',
        'config_path': '/home/Mike/projects/xenodx/xenodx_fulfillment/apis/behavior_signals/config/config.yaml',
        'description': 'Behavioral Signals emotion analysis API'
    },
    'hume_ai': {
        'client_class': 'HumeAIClient',
        'analyzer_class': 'HumeAIAnalyzer',
        'import_path': 'xenodx_fulfillment.apis.hume_ai.src',
        'config_path': '/home/Mike/projects/xenodex/xenodx_fulfillment/apis/hume_ai/config/config.yaml',
        'description': 'Hume AI emotion analysis API'
    }
}


def get_api_info(api_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific API
    
    Args:
        api_name: Name of the API
        
    Returns:
        API information dict or None if not found
    """
    return APIS.get(api_name)


def validate_api_name(api_name: str) -> bool:
    """
    Validate if an API name is registered
    
    Args:
        api_name: Name of the API to validate
        
    Returns:
        True if API is registered, False otherwise
    """
    return api_name in APIS


def list_available_apis() -> List[str]:
    """
    List all available API names
    
    Returns:
        List of available API names
    """
    return list(APIS.keys())