# Xenodex Fulfillment Quick Reference

## Directory Structure
```
xenodex_fulfillment/
├── process_data/        # Pre-API processing (empty - needs implementation)
├── apis/               # API integrations
│   ├── behavior_signals/   # Behavioral analysis API
│   └── _template/         # Template for new APIs
├── data/               # Shared data storage
├── reports/            # Top-level reports (easy access)
└── ai/                # AI models and analysis
```

## Key Paths

### Shared Data (all APIs use these)
- Downloads: `xenodex_fulfillment/data/downloads/`
- Converted: `xenodex_fulfillment/data/converted/`
- Samples: `xenodex_fulfillment/data/samples/`
- Chunks: `xenodex_fulfillment/data/chunks/`

### API-Specific
- Results: `xenodex_fulfillment/apis/{api_name}/results/`
- Reports: `xenodex_fulfillment/reports/{api_name}/`
- Config: `xenodex_fulfillment/apis/{api_name}/config/config.yaml`

## Quick Commands

### Run Behavior Signals Pipeline
```bash
cd xenodex_fulfillment/apis/behavior_signals
python scripts/run_pipeline.py --from-shared
```

### Add a New API
```bash
# 1. Copy template
cp -r apis/_template apis/your_new_api

# 2. Update configuration
vim apis/your_new_api/config/config.yaml

# 3. Set environment variables
export YOUR_API_KEY="your-key-here"
export YOUR_API_CLIENT_ID="your-client-id"

# 4. Test the API
python apis/your_new_api/scripts/test_api.py
```

### Process Multiple Files
```bash
# Behavior Signals batch processing
python apis/behavior_signals/scripts/run_pipeline.py file1.mp3 file2.mp3 --batch
```

## Configuration Files

### API Config Structure (`config/config.yaml`)
```yaml
api:
  key: "${API_KEY}"
  client_id: "${CLIENT_ID}"
  base_url: "https://api.example.com"

paths:
  shared_samples: "/absolute/path/to/samples"
  results: "./results"              # Relative to API dir
  reports: "../../reports/api_name" # Top-level reports

timeouts:
  max_wait: 600  # 10 minutes
```

### Environment Variables
```bash
# Behavior Signals
BEHAVIORAL_SIGNALS_API_KEY=xxx
BEHAVIORAL_SIGNALS_CLIENT_ID=xxx

# Your New API
YOUR_API_KEY=xxx
YOUR_API_CLIENT_ID=xxx
```

## File Naming Conventions

### Results
- Format: `{filename}_{timestamp}_results.json`
- Example: `video1_5min_20240810_143022_results.json`

### Reports  
- Format: `{filename}_report.txt`
- Example: `video1_5min_report.txt`

### Jobs
- Format: `job_{timestamp}.json`
- Example: `job_20240810_143022.json`

## Common Tasks

### 1. Process a YouTube Video
```bash
# Currently requires manual download and conversion
# TODO: Implement process_data workflows
```

### 2. Check API Status
```bash
# Behavior Signals
python apis/behavior_signals/scripts/run_pipeline.py --status job_id
```

### 3. Generate Report from Existing Results
```bash
python apis/behavior_signals/scripts/run_pipeline.py --report results/file.json
```

### 4. List Available Samples
```bash
ls -la data/samples/
```

## Troubleshooting

### Missing Samples
- Check: `data/samples/` directory
- Solution: Process media through `process_data` workflows (TODO)

### API Errors
- Check: API credentials in environment
- Check: `config/config.yaml` paths
- Test: `scripts/test_api.py`

### Path Errors
- Ensure absolute paths for shared data
- Use relative paths for API-specific directories

## Development Workflow

1. **Pre-process Media** (TODO: implement)
   ```bash
   python process_data/workflows/process_media.py "youtube_url"
   ```

2. **Run API Pipeline**
   ```bash
   python apis/{api_name}/scripts/run_pipeline.py --from-shared
   ```

3. **View Results**
   ```bash
   # JSON results
   cat apis/{api_name}/results/*.json
   
   # Human-readable reports  
   cat reports/{api_name}/*.txt
   ```

## Adding New Features

### To an Existing API
1. Update `src/api/client.py` with new methods
2. Extend `src/pipeline/pipeline.py` for new workflow
3. Update `src/analysis/report_generator.py` for new data
4. Add tests in `tests/`

### New Pre-Processing Step
1. Add to appropriate `process_data/` subdirectory
2. Update workflows to include new step
3. Document output format and location

## Important Notes

- **process_data is empty**: Needs implementation for downloading/converting
- **Shared data paths**: Must be absolute in config files
- **Environment variables**: Required for API credentials
- **Reports location**: Always at top level for easy access
- **Template available**: Use `_template` as starting point