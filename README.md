# Xenodex Fulfillment Process Data

This repository contains all pre-API processing files for the Xenodex fulfillment system. These files handle data downloading, conversion, extraction, and processing before making API calls.

## Directory Structure

```
/home/Mike/Xenodx/fulfillment/
├── process_data/          # All pre-API processing code
│   ├── workflows/         # Main workflow orchestration files
│   ├── downloaders/       # Download utilities for various sources
│   ├── extractors/        # Link and data extraction tools
│   ├── processors/        # Data processing and transformation
│   ├── converters/        # File conversion and maintenance
│   ├── storage/           # Storage management (S3, local)
│   ├── config/            # Configuration files
│   ├── utils/             # Supporting utilities
│   ├── monitoring/        # Progress tracking and monitoring
│   └── scripts/           # Standalone processing scripts
│
└── data/                  # All data storage (created at runtime)
    ├── output.csv         # Main output CSV file
    ├── drive_downloads/   # Google Drive downloaded files
    ├── youtube_downloads/ # YouTube downloaded content
    ├── simple_downloads/  # Simple download storage
    └── downloads/         # General downloads directory
```

## Key Files

### Workflows
- `workflows/simple_workflow.py` - Main 6-step workflow orchestrator
- `workflows/run_drive_downloads_async.py` - Async Google Drive downloads
- `workflows/run_youtube_downloads_async.py` - Async YouTube downloads
- `workflows/download_all_media.py` - Download all media from CSV
- `workflows/process_unprocessed_rows.py` - Process rows with missing data

### Downloaders
- `downloaders/download_drive.py` - Google Drive file downloading
- `downloaders/download_youtube.py` - YouTube video/audio downloading
- `downloaders/download_utils.py` - General download utilities
- `downloaders/download_drive_files_from_html.py` - HTML-based Drive downloads
- `downloaders/download_small_drive_files.py` - Small file downloads
- `downloaders/download_large_drive_files.py` - Large file downloads

### Extractors
- `extractors/extract_links.py` - Extract links from Google Docs
- `extractors/patterns.py` - URL pattern matching and cleaning
- `extractors/url_utils.py` - URL utilities and validation
- `extractors/run_extract_links.py` - Extract links workflow

### Processors
- `processors/data_processing.py` - Centralized data processing utilities

### Configuration
- `config/config.yaml` - Main configuration file with all paths updated

## Data Directory

All downloaded and processed data is stored in `/home/Mike/Xenodx/fulfillment/data/`:
- **output.csv**: Main CSV file containing all processed data
- **drive_downloads/**: Google Drive files organized by type
- **youtube_downloads/**: YouTube videos and transcripts
- **simple_downloads/**: Files from simple download operations
- **downloads/**: General download storage

## Usage

All files have been updated to:
1. Reference the new data directory at `/home/Mike/Xenodx/fulfillment/data/`
2. Import utilities from the original project location
3. Use absolute paths for all file operations

### Running Workflows

```bash
# Run the main workflow
python3 /home/Mike/Xenodx/fulfillment/process_data/workflows/simple_workflow.py

# Download YouTube content
python3 /home/Mike/Xenodx/fulfillment/process_data/workflows/run_youtube_downloads_async.py

# Download Google Drive files
python3 /home/Mike/Xenodx/fulfillment/process_data/workflows/run_drive_downloads_async.py
```

### Testing

A test script is included to verify all paths and imports are correctly configured:

```bash
python3 /home/Mike/Xenodx/fulfillment/test_paths.py
```

## Important Notes

1. All file paths have been updated to use absolute paths pointing to `/home/Mike/Xenodx/fulfillment/data/`
2. Import statements use the original project path: `/home/Mike/projects/xenodx/typing-clients-ingestion-minimal`
3. The configuration file at `config/config.yaml` contains all updated paths
4. Data directories are automatically created when needed

## Migration Complete

All pre-API processing files have been successfully:
- ✅ Moved to the new process_data directory
- ✅ Updated with correct file paths
- ✅ Updated with correct import statements
- ✅ Tested and verified to be working correctly

This represents a complete reorganization of the pre-API data processing pipeline, cleanly separated from the main API processing logic.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>