"""Shared pipeline orchestration for all API integrations"""
import asyncio
import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .models import APIClient, ResultAnalyzer, AnalysisResult
from .config import Config
from .reports import ReportGenerator
from .utils import validate_file


class Pipeline:
    """Generic pipeline for any API integration"""
    
    def __init__(self, client: APIClient, analyzer: ResultAnalyzer, config: Config):
        """
        Initialize pipeline with API-specific implementations
        
        Args:
            client: API client implementing APIClient protocol
            analyzer: Result analyzer implementing ResultAnalyzer protocol
            config: Configuration instance
        """
        self.client = client
        self.analyzer = analyzer
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.report_generator = ReportGenerator()
    
    async def process_file(self, file_path: Path) -> AnalysisResult:
        """
        Process a single file through the API
        
        Args:
            file_path: Path to file to process
            
        Returns:
            Analysis result
        """
        # Validate file
        file_path = validate_file(str(file_path))
        
        # Get error handling config
        error_config = self.config.get('error_handling', {})
        max_retries = error_config.get('max_retries', 3)
        retry_delay = error_config.get('retry_delay', 5)
        
        # Attempt processing with retries
        last_error = None
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Processing {file_path.name} (attempt {attempt + 1}/{max_retries})")
                
                # Call API
                start_time = time.time()
                raw_result = await self.client.analyze_file(file_path)
                processing_time = time.time() - start_time
                
                # Analyze results
                result = self.analyzer.analyze(raw_result)
                
                # Update metadata
                result.metadata.processing_time = processing_time
                
                self.logger.info(f"Successfully processed {file_path.name}")
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                
        # All retries failed
        raise Exception(f"Failed after {max_retries} attempts: {last_error}")
    
    def _save_job_info(self, job_info: Dict[str, Any]):
        """Save job information if job tracking enabled"""
        if not self.config.get('job_tracking.enable', True):
            return
        
        job_dir = Path(self.config.get('job_tracking.directory', 'jobs'))
        job_dir.mkdir(parents=True, exist_ok=True)
        
        job_file = job_dir / f"{job_info['job_id']}.json"
        with open(job_file, 'w') as f:
            json.dump(job_info, f, indent=2, default=str)
    
    def _generate_reports(self, result: AnalysisResult, job_id: str):
        """Generate reports in configured formats"""
        formats = self.config.get('reports.formats', ['json'])
        output_dir = Path(self.config.get('reports.output_directory', 'reports'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for format_type in formats:
            if format_type in ['json', 'html', 'markdown']:
                output_file = output_dir / f"{job_id}_analysis.{format_type}"
                self.report_generator.save_report(result, output_file, format=format_type)
                self.logger.info(f"Generated {format_type.upper()} report: {output_file}")
    
    def _handle_result(self, result: AnalysisResult, job_id: str):
        """Handle successful result"""
        # Save job info
        job_info = {
            'job_id': job_id,
            'status': 'completed',
            'timestamp': datetime.now(),
            'file_path': result.metadata.file_path,
            'api_name': result.metadata.api_name,
            'primary_emotion': result.get_primary_emotion().category.value if result.get_primary_emotion() else None
        }
        self._save_job_info(job_info)
        
        # Generate reports
        self._generate_reports(result, job_id)
    
    def run(self):
        """
        Run pipeline with CLI arguments
        
        This is the main entry point that handles:
        - Command line argument parsing
        - Async execution
        - Job tracking
        - Report generation
        """
        # Parse command line arguments
        if len(sys.argv) < 2:
            print(f"Usage: {sys.argv[0]} <audio/video file>")
            sys.exit(1)
        
        file_path = Path(sys.argv[1])
        
        # Generate job ID
        job_id = f"{self.config.get('api_name', 'api').lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Run async processing
        try:
            result = asyncio.run(self.process_file(file_path))
            self._handle_result(result, job_id)
            
            # Print summary
            primary = result.get_primary_emotion()
            if primary:
                print(f"\nPrimary emotion: {primary.category.value} ({primary.score:.0%})")
            if result.summary:
                print(f"Summary: {result.summary}")
            print(f"\nJob ID: {job_id}")
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            
            # Save failed job info
            job_info = {
                'job_id': job_id,
                'status': 'failed',
                'timestamp': datetime.now(),
                'file_path': str(file_path),
                'error': str(e)
            }
            self._save_job_info(job_info)
            
            sys.exit(1)