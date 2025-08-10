# Xenodex Fulfillment Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           XENODEX FULFILLMENT SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐        ┌────────────────────┐                     │
│  │   PROCESS_DATA      │        │       DATA         │                     │
│  │                     │        │                    │                     │
│  │ ┌─────────────────┐ │        │ ┌────────────────┐ │                     │
│  │ │   Downloaders   │ │───────▶│ │   downloads/   │ │                     │
│  │ └─────────────────┘ │        │ └────────────────┘ │                     │
│  │                     │        │                    │                     │
│  │ ┌─────────────────┐ │        │ ┌────────────────┐ │                     │
│  │ │   Extractors    │ │───────▶│ │   converted/   │ │                     │
│  │ └─────────────────┘ │        │ └────────────────┘ │                     │
│  │                     │        │                    │                     │
│  │ ┌─────────────────┐ │        │ ┌────────────────┐ │                     │
│  │ │   Processors    │ │───────▶│ │    samples/    │ │◀─────┐             │
│  │ └─────────────────┘ │        │ └────────────────┘ │      │             │
│  │                     │        │                    │      │             │
│  │ ┌─────────────────┐ │        │ ┌────────────────┐ │      │             │
│  │ │   Workflows     │ │───────▶│ │     chunks/    │ │      │             │
│  │ └─────────────────┘ │        │ └────────────────┘ │      │             │
│  └─────────────────────┘        └────────────────────┘      │             │
│                                                              │             │
│  ┌───────────────────────────────────────────────────────────┼─────────┐   │
│  │                              APIS                          │         │   │
│  │  ┌─────────────────────────────────────────────────────────┼──────┐  │   │
│  │  │                    behavior_signals/                    │      │  │   │
│  │  │  ┌─────────────┐    ┌──────────────┐    ┌────────────┐ │      │  │   │
│  │  │  │   Pipeline   │───▶│  API Client  │───▶│  External  │ │      │  │   │
│  │  │  │             │    │              │    │    API     │ │      │  │   │
│  │  │  └──────┬──────┘    └──────────────┘    └────────────┘ │      │  │   │
│  │  │         │                                              │      │  │   │
│  │  │         ▼                                              │      │  │   │
│  │  │  ┌─────────────┐                      ┌──────────────┐ │      │  │   │
│  │  │  │   results/   │                      │   Analysis   │ │      │  │   │
│  │  │  │   (JSON)    │─────────────────────▶│  & Reports   │ │      │  │   │
│  │  │  └─────────────┘                      └───────┬──────┘ │      │  │   │
│  │  └────────────────────────────────────────────────┼───────┘      │  │   │
│  │                                                   │              │  │   │
│  │  ┌─────────────────────────────────────────────────┼──────┐      │  │   │
│  │  │                    your_new_api/                │      │      │  │   │
│  │  │  ┌─────────────┐    ┌──────────────┐    ┌──────▼─────┐ │      │  │   │
│  │  │  │   Pipeline   │───▶│  API Client  │───▶│  External  │ │      │  │   │
│  │  │  │             │    │              │    │    API     │ │      │  │   │
│  │  │  └──────┬──────┘    └──────────────┘    └────────────┘ │      │  │   │
│  │  │         │                                              │      │  │   │
│  │  │         ▼                                              │      │  │   │
│  │  │  ┌─────────────┐                      ┌──────────────┐ │      │  │   │
│  │  │  │   results/   │                      │   Analysis   │ │      │  │   │
│  │  │  │   (JSON)    │─────────────────────▶│  & Reports   │ │      │  │   │
│  │  │  └─────────────┘                      └───────┬──────┘ │      │  │   │
│  │  └────────────────────────────────────────────────┼───────┘      │  │   │
│  └───────────────────────────────────────────────────┼──────────────┘  │   │
│                                                      │                 │   │
│  ┌───────────────────────────────────────────────────▼──────────────┐  │   │
│  │                           REPORTS                                │  │   │
│  │  ┌──────────────────────┐    ┌──────────────────────┐          │  │   │
│  │  │  behavior_signals/   │    │    your_new_api/    │          │  │   │
│  │  │  - analysis.txt      │    │  - report1.txt      │          │  │   │
│  │  │  - summary.txt       │    │  - report2.txt      │          │  │   │
│  │  └──────────────────────┘    └──────────────────────┘          │  │   │
│  └──────────────────────────────────────────────────────────────────┘  │   │
│                                                                        │   │
│  ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │                              AI                                  │  │   │
│  │  ┌──────────────────┐    ┌──────────────────┐                  │  │   │
│  │  │  F/T Detector    │    │  Di/De Detector  │                  │  │   │
│  │  └──────────────────┘    └──────────────────┘                  │  │   │
│  │                                                                 │  │   │
│  │  ┌────────────────────────────────────────────┐                │  │   │
│  │  │            Ensemble Logic                  │                │  │   │
│  │  └────────────────────────────────────────────┘                │  │   │
│  └──────────────────────────────────────────────────────────────────┘  │   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Pre-Processing (process_data)
```
YouTube URL → Downloader → MP4 file → Extractor → MP3 file → Processor → Samples/Chunks
```

### 2. API Processing (apis/*)
```
Samples → API Pipeline → External API → Results (JSON) → Analysis → Reports (TXT)
```

### 3. Report Generation
```
API Results → Analysis Engine → Human-Readable Reports → Top-Level Reports Directory
```

## Directory Purpose

### `/process_data`
- **Purpose**: Handle all media acquisition and preprocessing
- **Output**: Standardized audio files ready for API consumption
- **Shared**: All APIs use the same preprocessed data

### `/apis`
- **Purpose**: Individual API integrations
- **Independence**: Each API is self-contained
- **Structure**: Consistent pattern for easy addition of new APIs

### `/data`
- **Purpose**: Centralized data storage
- **Organization**: 
  - `downloads/`: Raw downloaded files
  - `converted/`: Format-converted files
  - `samples/`: Trimmed audio samples
  - `chunks/`: Split audio chunks
  - `jobs/`: Job tracking across all APIs

### `/reports`
- **Purpose**: Easy access to all generated reports
- **Organization**: Subdirectory per API
- **Access**: Top-level placement for quick navigation

### `/ai`
- **Purpose**: Machine learning models and analysis
- **Components**:
  - Personality detection models
  - Ensemble logic
  - Training and inference pipelines

## Key Design Decisions

1. **Shared Pre-Processing**
   - Eliminates duplicate downloading/conversion
   - Ensures consistent audio quality
   - Reduces storage requirements

2. **API Independence**
   - Each API can be developed/tested separately
   - No inter-API dependencies
   - Easy to add/remove APIs

3. **Results Co-location**
   - API results stored with the API that generated them
   - Clear ownership and organization
   - Simplifies debugging

4. **Top-Level Reports**
   - Reports easily accessible without navigating deep directories
   - Clear separation between technical results and user reports
   - Supports cross-API report generation

5. **Configuration Hierarchy**
   - Shared configuration in process_data
   - API-specific overrides in each API directory
   - Environment variable support for secrets

## Adding a New API

1. Copy the `_template` directory
2. Update configuration
3. Implement API client
4. Connect to shared data
5. Generate reports to top-level directory

See [ADDING_NEW_APIS.md](ADDING_NEW_APIS.md) for detailed instructions.