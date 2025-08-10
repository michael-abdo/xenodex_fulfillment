# Migration Guide: Converting Existing APIs to Shared Services

This guide walks through converting an existing API integration to use the xenodx_fulfillment shared services architecture.

## Overview

Migrating to shared services typically reduces code by 90% while improving maintainability, consistency, and feature availability. The migration process involves:

1. Analyzing existing code structure
2. Extracting API-specific logic
3. Implementing protocol interfaces
4. Removing duplicated code
5. Testing the migrated integration

## Before Migration Example

Typical existing API integration structure:
```
old_api_integration/
├── client.py          # 500+ lines: API calls, error handling, retries
├── analyzer.py        # 300+ lines: Result parsing, formatting
├── config.py          # 200+ lines: Configuration management
├── reports.py         # 400+ lines: Report generation
├── pipeline.py        # 300+ lines: Orchestration logic
├── utils.py           # 200+ lines: Utilities
└── main.py           # 100+ lines: Entry point
Total: ~2000 lines of code
```

## After Migration Example

Migrated API using shared services:
```
apis/your_api/
├── src/
│   ├── client.py      # 30-50 lines: Just API-specific calls
│   └── analyzer.py    # 30-50 lines: Just result mapping
├── config/
│   └── config.yaml    # 20 lines: Configuration
├── run_pipeline.py    # 20 lines: Boilerplate
└── requirements.txt   # API-specific dependencies only
Total: ~100-150 lines of code
```

## Step-by-Step Migration Process

### Step 1: Analyze Existing Code

First, identify the API-specific vs. generic functionality:

```python
# API-Specific (keep):
- API endpoint URLs
- Authentication methods
- Request/response formats
- Result parsing logic
- Emotion mapping rules

# Generic (remove - use shared services):
- Configuration loading
- Environment variable handling
- Retry logic
- Error handling
- Report generation
- File validation
- Logging setup
- CLI argument parsing
```

### Step 2: Create New Directory Structure

```bash
mkdir -p xenodx_fulfillment/apis/your_api/{src,config,results,jobs}
touch xenodx_fulfillment/apis/your_api/src/__init__.py
```

### Step 3: Extract and Implement API Client

Create `src/client.py` implementing the APIClient protocol:

```python
from typing import Dict, Any
from pathlib import Path
import aiohttp
from shared.models import APIClient

class YourAPIClient(APIClient):
    """Client for Your API - only API-specific logic"""
    
    def __init__(self, config: Dict[str, Any]):
        # Extract only what you need from config
        self.api_key = config['api_key']
        self.base_url = config.get('base_url', 'https://api.example.com')
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Send file to API for analysis"""
        # Copy ONLY the API-specific request logic
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=file_path.name)
                
                async with session.post(
                    f"{self.base_url}/analyze",
                    headers=headers,
                    data=data
                ) as response:
                    return await response.json()
```

**Migration tips:**
- Remove ALL error handling - shared pipeline handles it
- Remove retry logic - shared pipeline handles it
- Remove logging - shared pipeline handles it
- Keep ONLY the actual API call logic

### Step 4: Extract and Implement Result Analyzer

Create `src/analyzer.py` implementing the ResultAnalyzer protocol:

```python
from typing import Dict, Any, List
from datetime import datetime
from shared.models import (
    ResultAnalyzer, AnalysisResult, EmotionScore, 
    EmotionCategory, Metadata
)

class YourAPIAnalyzer(ResultAnalyzer):
    """Analyzer for Your API results - only parsing logic"""
    
    # Map API's emotion names to standard categories
    EMOTION_MAP = {
        'happiness': EmotionCategory.JOY,
        'sad': EmotionCategory.SADNESS,
        'angry': EmotionCategory.ANGER,
        'scared': EmotionCategory.FEAR,
        'surprised': EmotionCategory.SURPRISE,
        'disgusted': EmotionCategory.DISGUST,
        'calm': EmotionCategory.NEUTRAL,
    }
    
    def analyze(self, raw_result: Dict[str, Any]) -> AnalysisResult:
        """Convert raw API response to standardized format"""
        # Extract emotions from YOUR API's format
        emotions = []
        for emotion_data in raw_result.get('emotions', []):
            category = self.EMOTION_MAP.get(
                emotion_data['name'].lower(), 
                EmotionCategory.UNKNOWN
            )
            emotions.append(EmotionScore(
                category=category,
                score=emotion_data['score'],
                confidence=emotion_data.get('confidence', 1.0)
            ))
        
        # Build standardized result
        return AnalysisResult(
            emotions=emotions,
            raw_response=raw_result,
            metadata=Metadata(
                file_path=raw_result.get('file_path', ''),
                duration=raw_result.get('duration'),
                api_name="Your API",
                processing_time=raw_result.get('processing_time')
            ),
            summary=raw_result.get('summary')
        )
```

**Migration tips:**
- Remove ALL formatting logic - shared reports handle it
- Remove file I/O - shared pipeline handles it
- Focus on mapping YOUR API's format to standard format

### Step 5: Create Configuration

Create `config/config.yaml`:

```yaml
# API Configuration
api_name: "Your API Name"
api_key: "${YOUR_API_KEY}"  # From environment variable
base_url: "https://api.yourapi.com/v1"

# Copy these standard sections as-is
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

job_tracking:
  enable: true
  directory: "jobs"

reports:
  formats: ["html", "json", "markdown"]
  output_directory: "reports"

error_handling:
  max_retries: 3
  retry_delay: 5

# Add any API-specific config
your_api_specific:
  model_version: "v2"
  language: "en-US"
```

### Step 6: Create Entry Point

Create `run_pipeline.py` (copy this exactly):

```python
#!/usr/bin/env python3
"""Entry point for Your API integration"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.pipeline import Pipeline
from shared.config import Config
from shared.utils import setup_logging
from src.client import YourAPIClient
from src.analyzer import YourAPIAnalyzer

def main():
    # Load configuration
    config = Config.from_yaml("config/config.yaml")
    
    # Set up logging
    setup_logging(config.to_dict())
    
    # Create pipeline with your implementations
    pipeline = Pipeline(
        client=YourAPIClient(config.to_dict()),
        analyzer=YourAPIAnalyzer(),
        config=config
    )
    
    # Run pipeline
    pipeline.run()

if __name__ == "__main__":
    main()
```

### Step 7: Update Dependencies

Create minimal `requirements.txt`:

```
# Only API-specific dependencies
# Remove: pyyaml, python-dotenv, aiofiles, jinja2, etc.
# Those are in shared/requirements.txt

your-api-sdk==1.2.3
# Any other API-specific packages
```

### Step 8: Test the Migration

1. **Unit test your components:**

```python
# test_migration.py
from src.client import YourAPIClient
from src.analyzer import YourAPIAnalyzer

def test_analyzer():
    # Test with your API's actual response format
    mock_response = {
        "emotions": [
            {"name": "happiness", "score": 0.8, "confidence": 0.9}
        ],
        "duration": 120
    }
    
    analyzer = YourAPIAnalyzer()
    result = analyzer.analyze(mock_response)
    
    assert len(result.emotions) == 1
    assert result.emotions[0].category == EmotionCategory.JOY
    assert result.emotions[0].score == 0.8
```

2. **Integration test:**

```bash
cd apis/your_api
python run_pipeline.py /path/to/test/file.mp3
```

### Step 9: Remove Old Code

After confirming the migration works:

1. Delete all duplicated code files
2. Remove unnecessary dependencies
3. Update documentation

## Common Migration Patterns

### Pattern 1: Custom Authentication

If your API uses custom auth beyond Bearer tokens:

```python
class YourAPIClient(APIClient):
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']
    
    def _generate_auth_signature(self, timestamp: str) -> str:
        # Your custom auth logic
        return hmac.new(
            self.api_secret.encode(),
            f"{timestamp}{self.api_key}".encode(),
            hashlib.sha256
        ).hexdigest()
```

### Pattern 2: Streaming APIs

For APIs that stream results:

```python
async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
    # Accumulate streaming results
    results = []
    async for chunk in self._stream_analysis(file_path):
        results.append(chunk)
    
    # Return combined result
    return {"chunks": results, "status": "complete"}
```

### Pattern 3: Multi-Step Analysis

For APIs requiring multiple calls:

```python
async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
    # Step 1: Upload file
    upload_response = await self._upload_file(file_path)
    file_id = upload_response['id']
    
    # Step 2: Start analysis
    job_id = await self._start_analysis(file_id)
    
    # Step 3: Poll for results
    return await self._wait_for_results(job_id)
```

## Validation Checklist

After migration, verify:

- [ ] API client only contains API-specific logic (~50 lines)
- [ ] Analyzer only contains result mapping (~50 lines)
- [ ] No duplicated error handling code
- [ ] No duplicated retry logic
- [ ] No duplicated report generation
- [ ] No duplicated configuration parsing
- [ ] All tests pass
- [ ] Reports generate correctly
- [ ] Job tracking works

## Troubleshooting

### Issue: Import errors

```python
# Add to top of run_pipeline.py:
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
```

### Issue: Missing shared dependencies

```bash
cd xenodx_fulfillment
pip install -r shared/requirements.txt
```

### Issue: Config not loading

Ensure environment variables are set:
```bash
export YOUR_API_KEY="your-actual-key"
```

### Issue: Custom config needs

Add to config.yaml and access via:
```python
custom_value = config.get('your_api_specific.custom_field')
```

## Benefits After Migration

1. **Code Reduction**: ~2000 lines → ~150 lines (92% reduction)
2. **Maintenance**: Update shared services benefits all APIs
3. **Features**: Automatic access to new report formats, job tracking, etc.
4. **Testing**: Shared test infrastructure
5. **Consistency**: Same CLI interface for all APIs

## Next Steps

1. Run the validation script to ensure no duplication
2. Add API-specific documentation to `apis/your_api/README.md`
3. Consider contributing improvements to shared services
4. Share your migration experience with the team