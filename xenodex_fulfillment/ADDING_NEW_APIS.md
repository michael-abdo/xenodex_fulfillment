# Adding New APIs to Xenodex Fulfillment

This guide provides a comprehensive walkthrough for adding new API integrations to the Xenodex Fulfillment system. The structure is designed to maintain consistency, reusability, and clear separation of concerns.

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Step-by-Step Guide to Adding a New API](#step-by-step-guide-to-adding-a-new-api)
4. [Configuration Management](#configuration-management)
5. [Code Templates](#code-templates)
6. [Testing Your API](#testing-your-api)
7. [Documentation Requirements](#documentation-requirements)
8. [Best Practices](#best-practices)

## System Architecture Overview

The Xenodex Fulfillment system follows a clear architectural pattern:

```
xenodex_fulfillment/
├── process_data/          # Pre-API processing (downloads, conversions, sampling)
│   ├── config/           # Shared configuration
│   ├── downloaders/      # Media downloaders (YouTube, etc.)
│   ├── extractors/       # Audio/video extraction
│   ├── processors/       # Audio processing (trimming, chunking)
│   └── workflows/        # Orchestration scripts
│
├── apis/                 # API integrations
│   └── [api_name]/      # Your new API goes here
│
├── data/                # Shared data storage
│   ├── downloads/       # Original downloads
│   ├── converted/       # Converted media files
│   ├── samples/         # Processed samples
│   ├── chunks/          # Chunked audio files
│   ├── jobs/           # Job tracking
│   └── results/        # API results (legacy)
│
├── reports/            # Generated reports (top-level for easy access)
│   └── [api_name]/    # Reports for each API
│
└── ai/                # AI models and analysis
```

### Key Design Principles:
1. **Shared Data Processing**: All APIs use the same pre-processed data from `process_data/`
2. **API Independence**: Each API is self-contained in its own directory
3. **Results Co-location**: API results are stored within the API directory
4. **Report Accessibility**: Reports are at the top level for easy access
5. **Configuration Hierarchy**: APIs can override shared configurations

## Directory Structure

When adding a new API, create the following structure:

```
apis/
└── your_api_name/
    ├── README.md                    # API-specific documentation
    ├── requirements.txt             # API-specific dependencies
    ├── config/
    │   └── config.yaml             # API configuration
    ├── docs/
    │   ├── API_DESIGN.md          # Technical design documentation
    │   └── vendor_docs/           # Vendor API documentation
    ├── src/
    │   ├── __init__.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── client.py          # API client implementation
    │   │   ├── monitor.py         # Status monitoring
    │   │   └── models.py          # Data models/schemas
    │   ├── pipeline/
    │   │   ├── __init__.py
    │   │   ├── config.py          # Configuration loader
    │   │   └── pipeline.py        # Main orchestrator
    │   └── analysis/
    │       ├── __init__.py
    │       ├── analyzer.py        # Result analysis
    │       └── report_generator.py # Report creation
    ├── scripts/
    │   ├── run_pipeline.py        # Main entry point
    │   ├── test_api.py           # API testing script
    │   └── batch_process.py      # Batch processing
    ├── results/                   # API results storage
    └── tests/                     # Unit tests
        ├── __init__.py
        ├── test_client.py
        └── test_pipeline.py
```

## Step-by-Step Guide to Adding a New API

### Step 1: Create the Directory Structure

```bash
# Create your API directory
mkdir -p xenodex_fulfillment/apis/your_api_name/{config,docs,src/{api,pipeline,analysis},scripts,results,tests}

# Create __init__.py files
touch xenodex_fulfillment/apis/your_api_name/src/__init__.py
touch xenodex_fulfillment/apis/your_api_name/src/api/__init__.py
touch xenodex_fulfillment/apis/your_api_name/src/pipeline/__init__.py
touch xenodex_fulfillment/apis/your_api_name/src/analysis/__init__.py
touch xenodex_fulfillment/apis/your_api_name/tests/__init__.py

# Create reports directory
mkdir -p xenodex_fulfillment/reports/your_api_name
```

### Step 2: Create the Configuration File

Create `config/config.yaml`:

```yaml
# API credentials and endpoints
api:
  key: "${YOUR_API_KEY}"  # Use environment variables in production
  client_id: "${YOUR_CLIENT_ID}"
  base_url: "https://api.yourservice.com"
  version: "v1"
  
# API-specific timeouts
timeouts:
  api_submission: 120       # 2 minutes
  api_check_interval: 5     # 5 seconds
  max_wait: 600            # 10 minutes
  connection_timeout: 30    # Connection timeout
  read_timeout: 60         # Read timeout
  
# Path configuration
paths:
  # Shared data directory paths (processed by xenodex_fulfillment)
  shared_converted: "/home/Mike/projects/xenodex/xenodex_fulfillment/data/converted"
  shared_samples: "/home/Mike/projects/xenodex/xenodex_fulfillment/data/samples"
  shared_chunks: "/home/Mike/projects/xenodex/xenodex_fulfillment/data/chunks"
  
  # API-specific paths (relative to API directory)
  results: "./results"
  reports: "../../reports/your_api_name"
  jobs: "../data/jobs"

# Processing configuration
processing:
  supported_formats: ["mp3", "wav", "m4a"]
  max_file_size: 10485760  # 10MB
  default_sample_rate: 16000
  
# Feature flags
features:
  enable_chunking: true
  enable_batch_processing: true
  enable_retry: true
  max_retries: 3
```

### Step 3: Implement the API Client

Create `src/api/client.py`:

```python
"""API client for YourAPI service"""

import requests
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import time
import json

logger = logging.getLogger(__name__)


class YourAPIClient:
    """Client for interacting with YourAPI service"""
    
    def __init__(self, api_key: str, client_id: str, base_url: str):
        """Initialize the API client
        
        Args:
            api_key: API authentication key
            client_id: Client identifier
            base_url: Base URL for API endpoints
        """
        self.api_key = api_key
        self.client_id = client_id
        self.base_url = base_url.rstrip('/')
        
        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Client-ID': client_id,
            'Content-Type': 'application/json'
        })
        
    def submit_audio(self, audio_path: Path, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Submit audio file for processing
        
        Args:
            audio_path: Path to audio file
            metadata: Optional metadata for the submission
            
        Returns:
            Dict containing submission response with job_id
        """
        logger.info(f"Submitting audio file: {audio_path}")
        
        # Prepare the multipart form data
        with open(audio_path, 'rb') as f:
            files = {'audio': (audio_path.name, f, 'audio/mpeg')}
            data = {'metadata': json.dumps(metadata or {})}
            
            # Temporarily remove Content-Type for multipart
            headers = self.session.headers.copy()
            headers.pop('Content-Type', None)
            
            response = self.session.post(
                f"{self.base_url}/submit",
                files=files,
                data=data,
                headers=headers
            )
            
        response.raise_for_status()
        return response.json()
        
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check processing status
        
        Args:
            job_id: Job identifier from submission
            
        Returns:
            Dict containing status information
        """
        response = self.session.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()
        
    def get_results(self, job_id: str) -> Dict[str, Any]:
        """Retrieve processing results
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dict containing analysis results
        """
        response = self.session.get(f"{self.base_url}/results/{job_id}")
        response.raise_for_status()
        return response.json()
        
    def wait_for_completion(self, job_id: str, max_wait: int = 600, 
                          check_interval: int = 5) -> Dict[str, Any]:
        """Wait for job completion and return results
        
        Args:
            job_id: Job identifier
            max_wait: Maximum seconds to wait
            check_interval: Seconds between status checks
            
        Returns:
            Dict containing final results
            
        Raises:
            TimeoutError: If processing doesn't complete within max_wait
        """
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            status = self.check_status(job_id)
            
            if status['status'] == 'completed':
                return self.get_results(job_id)
            elif status['status'] == 'failed':
                raise Exception(f"Processing failed: {status.get('error', 'Unknown error')}")
                
            logger.info(f"Job {job_id} status: {status['status']}")
            time.sleep(check_interval)
            
        raise TimeoutError(f"Processing timeout after {max_wait} seconds")
```

### Step 4: Implement the Pipeline

Create `src/pipeline/pipeline.py`:

```python
"""Main pipeline orchestrator for YourAPI processing"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..api.client import YourAPIClient
from ..analysis.report_generator import ReportGenerator
from .config import Config

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the complete processing pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize pipeline with configuration"""
        self.config = Config(config_path)
        
        # Initialize API client
        api_config = self.config.api
        self.api_client = YourAPIClient(
            api_key=api_config['key'],
            client_id=api_config['client_id'],
            base_url=api_config['base_url']
        )
        
        # Initialize paths
        self.shared_samples = Path(self.config.paths['shared_samples'])
        self.results_dir = Path(self.config.paths['results'])
        self.reports_dir = Path(self.config.paths['reports'])
        
        # Ensure directories exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def process_audio(self, audio_filename: str) -> Dict[str, Any]:
        """Process a single audio file through the pipeline
        
        Args:
            audio_filename: Name of audio file in shared samples directory
            
        Returns:
            Dict containing processing results and paths
        """
        logger.info(f"Starting pipeline for: {audio_filename}")
        
        # Find audio file in shared samples
        audio_path = self.shared_samples / audio_filename
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        # Submit to API
        submission = self.api_client.submit_audio(audio_path)
        job_id = submission['job_id']
        logger.info(f"Submitted job: {job_id}")
        
        # Wait for completion
        results = self.api_client.wait_for_completion(
            job_id,
            max_wait=self.config.timeouts['max_wait'],
            check_interval=self.config.timeouts['api_check_interval']
        )
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"{audio_filename}_{timestamp}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved results to: {results_file}")
        
        # Generate report
        report_gen = ReportGenerator(self.config)
        report_path = report_gen.generate_report(results, audio_filename)
        logger.info(f"Generated report: {report_path}")
        
        return {
            'status': 'completed',
            'job_id': job_id,
            'results_file': str(results_file),
            'report_file': str(report_path),
            'results': results
        }
        
    def process_batch(self, audio_files: List[str]) -> List[Dict[str, Any]]:
        """Process multiple audio files
        
        Args:
            audio_files: List of audio filenames
            
        Returns:
            List of processing results
        """
        results = []
        for audio_file in audio_files:
            try:
                result = self.process_audio(audio_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {e}")
                results.append({
                    'status': 'failed',
                    'audio_file': audio_file,
                    'error': str(e)
                })
        return results
```

### Step 5: Create the Main Script

Create `scripts/run_pipeline.py`:

```python
#!/usr/bin/env python3
"""
Main entry point for YourAPI pipeline

Usage:
    python run_pipeline.py <audio_file>
    python run_pipeline.py --batch <file1> <file2> ...
    python run_pipeline.py --from-shared
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Process audio through YourAPI')
    parser.add_argument('audio_files', nargs='*', help='Audio files to process')
    parser.add_argument('--batch', action='store_true', help='Process multiple files')
    parser.add_argument('--from-shared', action='store_true', 
                       help='List and select from shared samples')
    parser.add_argument('--config', help='Path to config file')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = Pipeline(args.config)
    
    # Handle --from-shared option
    if args.from_shared:
        shared_dir = Path(pipeline.config.paths['shared_samples'])
        audio_files = list(shared_dir.glob('*.mp3'))
        
        if not audio_files:
            logger.error("No audio files found in shared samples directory")
            return 1
            
        print("\nAvailable audio files:")
        for i, file in enumerate(audio_files):
            print(f"{i+1}. {file.name}")
            
        selection = input("\nEnter file number(s) to process (comma-separated): ")
        indices = [int(x.strip())-1 for x in selection.split(',')]
        args.audio_files = [audio_files[i].name for i in indices]
        
    if not args.audio_files:
        parser.error("No audio files specified")
        
    # Process files
    try:
        if len(args.audio_files) == 1:
            result = pipeline.process_audio(args.audio_files[0])
            print(f"\nProcessing complete!")
            print(f"Results: {result['results_file']}")
            print(f"Report: {result['report_file']}")
        else:
            results = pipeline.process_batch(args.audio_files)
            success = sum(1 for r in results if r['status'] == 'completed')
            print(f"\nBatch processing complete: {success}/{len(results)} successful")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

### Step 6: Create the Report Generator

Create `src/analysis/report_generator.py`:

```python
"""Report generation for YourAPI results"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class ReportGenerator:
    """Generates human-readable reports from API results"""
    
    def __init__(self, config):
        self.config = config
        self.reports_dir = Path(config.paths['reports'])
        
    def generate_report(self, results: Dict[str, Any], audio_filename: str) -> Path:
        """Generate a report from API results
        
        Args:
            results: API results dictionary
            audio_filename: Original audio filename
            
        Returns:
            Path to generated report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create report content
        report_lines = [
            f"YourAPI Analysis Report",
            f"=" * 50,
            f"",
            f"Generated: {timestamp}",
            f"Audio File: {audio_filename}",
            f"",
            f"ANALYSIS RESULTS",
            f"-" * 30,
            f""
        ]
        
        # Add your specific result formatting here
        # Example:
        if 'transcription' in results:
            report_lines.extend([
                "Transcription:",
                results['transcription'],
                ""
            ])
            
        if 'analysis' in results:
            report_lines.extend([
                "Analysis:",
                json.dumps(results['analysis'], indent=2),
                ""
            ])
            
        # Save report
        report_filename = f"{audio_filename}_report.txt"
        report_path = self.reports_dir / report_filename
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
            
        return report_path
```

## Configuration Management

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# API Credentials
YOUR_API_KEY=your-api-key-here
YOUR_CLIENT_ID=your-client-id-here

# Optional overrides
YOUR_API_BASE_URL=https://api.yourservice.com
```

### Configuration Loader

Create `src/pipeline/config.py`:

```python
"""Configuration management for YourAPI"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Manages configuration for the pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Load configuration from file and environment"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
            
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
            
        # Override with environment variables
        self._apply_env_overrides()
        
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        # API credentials
        if api_key := os.getenv('YOUR_API_KEY'):
            self._config['api']['key'] = api_key
        if client_id := os.getenv('YOUR_CLIENT_ID'):
            self._config['api']['client_id'] = client_id
        if base_url := os.getenv('YOUR_API_BASE_URL'):
            self._config['api']['base_url'] = base_url
            
    @property
    def api(self) -> Dict[str, Any]:
        return self._config['api']
        
    @property
    def timeouts(self) -> Dict[str, Any]:
        return self._config['timeouts']
        
    @property
    def paths(self) -> Dict[str, Any]:
        return self._config['paths']
        
    @property
    def processing(self) -> Dict[str, Any]:
        return self._config.get('processing', {})
        
    @property
    def features(self) -> Dict[str, Any]:
        return self._config.get('features', {})
```

## Testing Your API

### Unit Tests

Create `tests/test_client.py`:

```python
"""Tests for YourAPI client"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.api.client import YourAPIClient


class TestYourAPIClient:
    """Test cases for API client"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return YourAPIClient(
            api_key="test-key",
            client_id="test-client",
            base_url="https://api.test.com"
        )
        
    def test_submit_audio(self, client, tmp_path):
        """Test audio submission"""
        # Create dummy audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"dummy audio data")
        
        with patch.object(client.session, 'post') as mock_post:
            mock_post.return_value.json.return_value = {'job_id': '12345'}
            
            result = client.submit_audio(audio_file)
            
            assert result['job_id'] == '12345'
            mock_post.assert_called_once()
            
    def test_check_status(self, client):
        """Test status checking"""
        with patch.object(client.session, 'get') as mock_get:
            mock_get.return_value.json.return_value = {
                'status': 'processing',
                'progress': 50
            }
            
            status = client.check_status('12345')
            
            assert status['status'] == 'processing'
            assert status['progress'] == 50
```

### Integration Test Script

Create `scripts/test_api.py`:

```python
#!/usr/bin/env python3
"""Test script for API integration"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.api.client import YourAPIClient
from src.pipeline.config import Config


def test_api_connection():
    """Test basic API connectivity"""
    config = Config()
    client = YourAPIClient(
        api_key=config.api['key'],
        client_id=config.api['client_id'],
        base_url=config.api['base_url']
    )
    
    # Test endpoint connectivity
    try:
        # Implement a simple health check
        response = client.session.get(f"{client.base_url}/health")
        response.raise_for_status()
        print("✓ API connection successful")
        return True
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        return False


def test_sample_processing():
    """Test processing a sample file"""
    # Find a small test file
    shared_samples = Path(Config().paths['shared_samples'])
    test_files = list(shared_samples.glob('*.mp3'))[:1]
    
    if not test_files:
        print("✗ No test files found in shared samples")
        return False
        
    print(f"Testing with: {test_files[0].name}")
    
    # Run pipeline
    from src.pipeline.pipeline import Pipeline
    pipeline = Pipeline()
    
    try:
        result = pipeline.process_audio(test_files[0].name)
        print("✓ Sample processing successful")
        print(f"  Results: {result['results_file']}")
        print(f"  Report: {result['report_file']}")
        return True
    except Exception as e:
        print(f"✗ Sample processing failed: {e}")
        return False


if __name__ == '__main__':
    print("Testing YourAPI Integration")
    print("-" * 30)
    
    tests = [
        test_api_connection,
        test_sample_processing
    ]
    
    passed = sum(test() for test in tests)
    print(f"\nPassed {passed}/{len(tests)} tests")
```

## Documentation Requirements

### 1. README.md (API-specific)

Create a comprehensive README for your API:

```markdown
# YourAPI Integration

Brief description of what YourAPI does and its purpose in the Xenodex system.

## Features

- List key features
- Supported formats
- Processing capabilities

## Quick Start

```bash
# Process a single file
python scripts/run_pipeline.py audio_file.mp3

# Process from shared samples
python scripts/run_pipeline.py --from-shared

# Batch processing
python scripts/run_pipeline.py --batch file1.mp3 file2.mp3
```

## Configuration

See `config/config.yaml` for configuration options.

Required environment variables:
- `YOUR_API_KEY`: API authentication key
- `YOUR_CLIENT_ID`: Client identifier

## API Limits

- Maximum file size: 10MB
- Supported formats: MP3, WAV
- Rate limits: X requests per minute

## Output

Results are saved to:
- JSON results: `results/`
- Human-readable reports: `../../reports/your_api_name/`
```

### 2. API_DESIGN.md

Document the technical design:

```markdown
# YourAPI Technical Design

## Architecture Overview

Describe how your API integration works within the Xenodex system.

## Data Flow

1. Audio file retrieved from shared samples
2. File submitted to YourAPI
3. Status monitored until completion
4. Results retrieved and saved
5. Report generated from results

## API Endpoints Used

- `POST /submit` - Submit audio for processing
- `GET /status/{job_id}` - Check processing status
- `GET /results/{job_id}` - Retrieve results

## Error Handling

- Network errors: Retry with exponential backoff
- API errors: Log and report specific error codes
- File errors: Validate before submission

## Performance Considerations

- Concurrent processing limits
- Optimal chunk sizes
- Caching strategies
```

## Best Practices

### 1. Error Handling

Always implement comprehensive error handling:

```python
try:
    result = api_client.submit_audio(audio_path)
except requests.exceptions.ConnectionError:
    logger.error("Network connection failed")
    # Implement retry logic
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        logger.warning("Rate limit exceeded, waiting...")
        # Implement backoff
    else:
        logger.error(f"API error: {e}")
        raise
```

### 2. Logging

Use structured logging throughout:

```python
logger.info("Processing started", extra={
    'audio_file': audio_filename,
    'job_id': job_id,
    'timestamp': datetime.now().isoformat()
})
```

### 3. Configuration Validation

Validate configuration on startup:

```python
def validate_config(config):
    """Validate required configuration"""
    required = ['api.key', 'api.client_id', 'api.base_url']
    for key in required:
        if not get_nested(config._config, key):
            raise ValueError(f"Missing required config: {key}")
```

### 4. Path Management

Use Path objects consistently:

```python
# Good
audio_path = Path(self.config.paths['shared_samples']) / audio_filename

# Avoid
audio_path = self.config.paths['shared_samples'] + '/' + audio_filename
```

### 5. Result Storage

Follow naming conventions:

```python
# Results: {audio_filename}_{timestamp}_results.json
results_file = f"{audio_filename}_{timestamp}_results.json"

# Reports: {audio_filename}_report.txt
report_file = f"{audio_filename}_report.txt"
```

### 6. Testing

Include tests for:
- API client methods
- Pipeline orchestration
- Error scenarios
- Configuration loading
- Report generation

### 7. Documentation

Keep documentation updated:
- API changes
- New features
- Configuration options
- Known issues

## Checklist for New API Integration

- [ ] Directory structure created
- [ ] Configuration file with all required settings
- [ ] API client with authentication and core methods
- [ ] Pipeline orchestrator using shared data
- [ ] Report generator for human-readable output
- [ ] Main script with CLI interface
- [ ] Unit tests for core functionality
- [ ] Integration test script
- [ ] README.md with usage instructions
- [ ] API_DESIGN.md with technical details
- [ ] Requirements.txt with dependencies
- [ ] Error handling and logging throughout
- [ ] Results stored in API directory
- [ ] Reports saved to top-level reports directory

## Common Patterns

### Chunking Support

If your API has size limits, implement chunking:

```python
def process_with_chunks(self, audio_path: Path, chunk_duration: int = 120):
    """Process audio in chunks"""
    chunks = self.split_audio(audio_path, chunk_duration)
    results = []
    
    for chunk in chunks:
        result = self.api_client.submit_audio(chunk)
        results.append(result)
        
    return self.merge_results(results)
```

### Batch Processing

For efficiency with multiple files:

```python
def process_batch_parallel(self, audio_files: List[str], max_workers: int = 5):
    """Process multiple files in parallel"""
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(self.process_audio, f): f 
            for f in audio_files
        }
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Failed: {futures[future]} - {e}")
                
    return results
```

### Caching Results

Avoid reprocessing:

```python
def get_cached_result(self, audio_filename: str) -> Optional[Dict]:
    """Check for existing results"""
    pattern = f"{audio_filename}_*_results.json"
    existing = list(self.results_dir.glob(pattern))
    
    if existing:
        # Return most recent
        latest = max(existing, key=lambda p: p.stat().st_mtime)
        with open(latest) as f:
            return json.load(f)
    return None
```

## Summary

This structure ensures:
1. **Consistency**: All APIs follow the same patterns
2. **Reusability**: Shared data and common utilities
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Easy to add new APIs
5. **Accessibility**: Reports easily accessible at top level

By following this guide, new API integrations will fit seamlessly into the Xenodex Fulfillment system while maintaining high code quality and user experience.