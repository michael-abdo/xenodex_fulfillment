# API Integration Template - Shared Services Architecture

This template demonstrates how to create a new API integration using the xenodx_fulfillment shared services architecture.

## Overview

Our shared services architecture reduces code duplication by ~90% across API integrations. Each API only needs to implement 3 core files:

1. **client.py** - API-specific client implementation
2. **analyzer.py** - API-specific result analysis logic  
3. **config.yaml** - API configuration

All common functionality is handled by shared services in `xenodx_fulfillment/shared/`.

## Creating a New API Integration

### 1. Directory Structure

```
xenodx_fulfillment/apis/your_api_name/
├── config/
│   └── config.yaml       # API configuration
├── src/
│   ├── __init__.py
│   ├── client.py         # Implements APIClient protocol
│   └── analyzer.py       # Implements ResultAnalyzer protocol
├── run_pipeline.py       # Entry point (minimal boilerplate)
├── requirements.txt      # API-specific dependencies only
└── README.md            # API documentation
```

### 2. Implement the APIClient Protocol

Create `src/client.py`:

```python
from typing import Dict, Any
from pathlib import Path
from shared.models import APIClient

class YourAPIClient(APIClient):
    """Client for interacting with Your API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['api_key']
        self.base_url = config.get('base_url', 'https://api.yourapi.com')
        # Initialize other config values
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Send file to API for analysis"""
        # Implement your API call logic here
        # Return raw API response
        pass
```

### 3. Implement the ResultAnalyzer Protocol

Create `src/analyzer.py`:

```python
from typing import Dict, Any, List
from shared.models import ResultAnalyzer, AnalysisResult, EmotionCategory

class YourAPIAnalyzer(ResultAnalyzer):
    """Analyzer for Your API results"""
    
    def analyze(self, raw_result: Dict[str, Any]) -> AnalysisResult:
        """Convert raw API response to standardized AnalysisResult"""
        # Extract relevant data from API response
        # Map to EmotionCategory enum values
        # Return AnalysisResult object
        pass
    
    def extract_emotions(self, raw_result: Dict[str, Any]) -> List[EmotionCategory]:
        """Extract emotion categories from results"""
        # Helper method to categorize emotions
        pass
```

### 4. Create Configuration

Create `config/config.yaml`:

```yaml
api_name: "Your API"
api_key: "${YOUR_API_KEY}"  # Environment variable
base_url: "https://api.yourapi.com"

# Logging configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Job tracking
job_tracking:
  enable: true
  directory: "jobs"

# Report generation
reports:
  formats: ["html", "json", "markdown"]
  output_directory: "reports"

# Error handling
error_handling:
  max_retries: 3
  retry_delay: 5
```

### 5. Create Entry Point

Create `run_pipeline.py`:

```python
#!/usr/bin/env python3
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
    
    # Run pipeline (handles CLI args, job tracking, reports)
    pipeline.run()

if __name__ == "__main__":
    main()
```

### 6. Add API-Specific Dependencies

Create `requirements.txt` with only API-specific dependencies:

```
# Only include dependencies specific to your API
# Shared dependencies are in xenodx_fulfillment/shared/requirements.txt
your-api-sdk==1.0.0
```

## Shared Services Available

The following services are automatically available to your API:

### 1. **Configuration Management** (`shared.config`)
- YAML loading with environment variable substitution
- Validation and type safety
- Automatic configuration merging

### 2. **Pipeline Orchestration** (`shared.pipeline`)
- CLI argument parsing
- Job tracking and persistence
- Error handling and retries
- Progress reporting

### 3. **Report Generation** (`shared.reports`)
- Multi-format output (HTML, JSON, Markdown)
- Consistent report structure
- Automatic file saving

### 4. **Utilities** (`shared.utils`)
- Logging setup
- File validation
- Common helper functions
- Documentation scraping

### 5. **Data Models** (`shared.models`)
- Standardized result formats
- Emotion categorization enum
- Type-safe protocols

## Best Practices

1. **Keep it Simple**: Only implement what's unique to your API
2. **Use Protocols**: Implement APIClient and ResultAnalyzer protocols
3. **Standardize Output**: Always return AnalysisResult objects
4. **Handle Errors**: Let shared services handle retries and logging
5. **Document Well**: Focus docs on API-specific behavior

## Testing Your Integration

1. Create a test file:
```python
from src.client import YourAPIClient
from src.analyzer import YourAPIAnalyzer
from shared.models import AnalysisResult

# Test with mock data
mock_response = {"your": "api", "response": "here"}
analyzer = YourAPIAnalyzer()
result = analyzer.analyze(mock_response)
assert isinstance(result, AnalysisResult)
```

2. Run the pipeline:
```bash
python run_pipeline.py path/to/test/file.mp3
```

## Common Patterns

### Emotion Mapping
```python
emotion_map = {
    "happiness": EmotionCategory.JOY,
    "sadness": EmotionCategory.SADNESS,
    "anger": EmotionCategory.ANGER,
    # Map API-specific emotions to standard categories
}
```

### Async File Upload
```python
async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f)
            async with session.post(self.base_url, data=data) as response:
                return await response.json()
```

## Support

For questions about shared services, see `/xenodx_fulfillment/shared/README.md`.
For examples, look at existing integrations in `/xenodx_fulfillment/apis/`.