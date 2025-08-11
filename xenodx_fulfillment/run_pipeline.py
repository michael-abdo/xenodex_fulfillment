#!/usr/bin/env python3
"""Unified entry point for all API integrations using shared services"""

import sys
import os
import asyncio
import importlib
import argparse
from pathlib import Path
from typing import Optional, Any, Dict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import shared services
from xenodx_fulfillment.shared.api_registry import (
    get_api_info, 
    validate_api_name, 
    list_available_apis
)
from xenodx_fulfillment.shared.config import Config
from xenodx_fulfillment.shared.pipeline import Pipeline
from xenodx_fulfillment.shared.models import APIClient, ResultAnalyzer


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Unified entry point for all API integrations using shared services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py --api behavior_signals audio.mp3
  python run_pipeline.py --api hume_ai recording.wav
  python run_pipeline.py --list-apis

Available APIs:
  behavior_signals    Behavioral Signals emotion analysis API  
  hume_ai            Hume AI emotion analysis API
        """
    )
    
    parser.add_argument(
        '--api',
        choices=list_available_apis(),
        required=False,
        help='API to use for analysis (required unless using --list-apis)'
    )
    
    parser.add_argument(
        'file_path',
        nargs='?',
        type=Path,
        help='Path to audio file for analysis'
    )
    
    parser.add_argument(
        '--list-apis',
        action='store_true',
        help='List all available APIs and exit'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Custom config file path (optional)'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['json', 'html', 'markdown'],
        default='json',
        help='Output format for results (default: json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def import_client_class(api_name: str) -> Optional[type]:
    """
    Dynamically import the client class for the specified API
    
    Args:
        api_name: Name of the API
        
    Returns:
        Client class or None if import fails
    """
    api_info = get_api_info(api_name)
    if not api_info:
        return None
    
    try:
        module_path = f"{api_info['import_path']}.client"
        class_name = api_info['client_class']
        
        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the class from the module
        client_class = getattr(module, class_name)
        
        return client_class
        
    except ImportError as e:
        print(f"Error importing client module {module_path}: {e}")
        return None
    except AttributeError as e:
        print(f"Error finding client class {class_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error importing client class: {e}")
        return None


def import_analyzer_class(api_name: str) -> Optional[type]:
    """
    Dynamically import the analyzer class for the specified API
    
    Args:
        api_name: Name of the API
        
    Returns:
        Analyzer class or None if import fails
    """
    api_info = get_api_info(api_name)
    if not api_info:
        return None
    
    try:
        module_path = f"{api_info['import_path']}.analyzer"
        class_name = api_info['analyzer_class']
        
        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the class from the module
        analyzer_class = getattr(module, class_name)
        
        return analyzer_class
        
    except ImportError as e:
        print(f"Error importing analyzer module {module_path}: {e}")
        return None
    except AttributeError as e:
        print(f"Error finding analyzer class {class_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error importing analyzer class: {e}")
        return None


def resolve_config_path(api_name: str, custom_config_path: Optional[Path] = None) -> Optional[Path]:
    """
    Resolve the configuration file path for the specified API
    
    Args:
        api_name: Name of the API
        custom_config_path: Optional custom config path provided by user
        
    Returns:
        Path to config file or None if not found
    """
    # Use custom config if provided
    if custom_config_path:
        if custom_config_path.exists():
            return custom_config_path
        else:
            print(f"Warning: Custom config file not found: {custom_config_path}")
            print("Falling back to default config...")
    
    # Get default config path from registry
    api_info = get_api_info(api_name)
    if not api_info:
        return None
    
    default_config_path = Path(api_info['config_path'])
    
    # Check if default config exists
    if default_config_path.exists():
        return default_config_path
    else:
        print(f"Error: Default config file not found: {default_config_path}")
        return None


def main():
    """Main entry point for unified pipeline"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Handle --list-apis option
    if args.list_apis:
        print("Available APIs:")
        for api_name in list_available_apis():
            api_info = get_api_info(api_name)
            print(f"  {api_name:<16} {api_info['description']}")
        return 0
    
    # Validate API parameter
    if not args.api:
        print("Error: --api parameter is required")
        parser.print_help()
        return 1
    
    if not validate_api_name(args.api):
        print(f"Error: Invalid API name '{args.api}'")
        print(f"Available APIs: {', '.join(list_available_apis())}")
        return 1
    
    # Validate file path parameter
    if not args.file_path:
        print("Error: file_path parameter is required")
        parser.print_help()
        return 1
    
    # Check if file exists and is accessible
    if not args.file_path.exists():
        print(f"Error: File not found: {args.file_path}")
        return 1
    
    if not args.file_path.is_file():
        print(f"Error: Path is not a file: {args.file_path}")
        return 1
    
    # Check file extension (optional validation)
    supported_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
    if args.file_path.suffix.lower() not in supported_extensions:
        print(f"Warning: File extension '{args.file_path.suffix}' may not be supported")
        print(f"Supported extensions: {', '.join(sorted(supported_extensions))}")
    
    # Set up verbose logging if requested
    if args.verbose:
        print(f"Selected API: {args.api}")
        api_info = get_api_info(args.api)
        print(f"Description: {api_info['description']}")
        print(f"Input file: {args.file_path}")
        print(f"File size: {args.file_path.stat().st_size} bytes")
        print(f"Output format: {args.output_format}")
    
    # Import API classes dynamically
    if args.verbose:
        print("Importing API classes...")
    
    client_class = import_client_class(args.api)
    if not client_class:
        print(f"Error: Failed to import client class for {args.api}")
        return 1
    
    analyzer_class = import_analyzer_class(args.api)
    if not analyzer_class:
        print(f"Error: Failed to import analyzer class for {args.api}")
        return 1
    
    # Resolve config path
    config_path = resolve_config_path(args.api, args.config)
    if not config_path:
        print(f"Error: Could not resolve config path for {args.api}")
        return 1
    
    if args.verbose:
        print(f"Using config: {config_path}")
    
    try:
        # Load configuration
        config = Config.from_yaml(str(config_path))
        
        # Create client and analyzer instances
        client = client_class(config.to_dict())
        # Some analyzers don't require config in initialization
        try:
            analyzer = analyzer_class(config.to_dict())
        except TypeError:
            analyzer = analyzer_class()
        
        # Create pipeline
        pipeline = Pipeline(client=client, analyzer=analyzer, config=config)
        
        if args.verbose:
            print("Pipeline created successfully")
            print(f"Starting analysis of {args.file_path}...")
        
        # Run the analysis asynchronously
        result = asyncio.run(pipeline.process_file(args.file_path))
        
        if args.verbose:
            print("Analysis completed successfully")
        
        # Generate report
        from xenodx_fulfillment.shared.reports import ReportGenerator
        report_generator = ReportGenerator()
        
        if args.output_format == 'json':
            output = report_generator.generate_report(result, format='json')
            print(output)
        elif args.output_format == 'html':
            output = report_generator.generate_report(result, format='html')
            print(output)
        elif args.output_format == 'markdown':
            output = report_generator.generate_report(result, format='markdown')
            print(output)
        
        if args.verbose:
            print(f"\nAnalysis complete! Results generated in {args.output_format} format.")
        
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())