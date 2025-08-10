#!/usr/bin/env python3
"""Entry point for Behavioral Signals API integration using shared services"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from xenodx_fulfillment.shared.pipeline import Pipeline
from xenodx_fulfillment.shared.config import Config
from xenodx_fulfillment.shared.utils import setup_logging
from src.client import BehavioralSignalsClient
from src.analyzer import BehavioralSignalsAnalyzer


def main():
    """Main entry point"""
    # Load configuration
    config = Config.from_yaml("config/config.yaml")
    
    # Set up logging using shared services
    setup_logging(config.to_dict())
    
    # Create pipeline with Behavioral Signals implementations
    pipeline = Pipeline(
        client=BehavioralSignalsClient(config.to_dict()),
        analyzer=BehavioralSignalsAnalyzer(),
        config=config
    )
    
    # Run pipeline (handles CLI args, job tracking, reports)
    pipeline.run()


if __name__ == "__main__":
    main()