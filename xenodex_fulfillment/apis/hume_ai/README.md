# API Template

This is a template directory for creating new API integrations. 

## Usage

1. Copy this entire `_template` directory to your new API name:
   ```bash
   cp -r _template your_api_name
   ```

2. Replace all instances of:
   - `YourAPI` with your API name (e.g., `BehaviorSignals`)
   - `your_api_name` with your API directory name (e.g., `behavior_signals`)
   - `YOUR_API` with your environment variable prefix (e.g., `BEHAVIOR_SIGNALS`)

3. Update the configuration file with your API endpoints and credentials

4. Implement the client methods for your specific API

5. Customize the report generator for your API's output format

6. Update this README with your API-specific documentation

## Structure

- `config/` - Configuration files
- `docs/` - API documentation
- `src/` - Source code
  - `api/` - API client implementation
  - `pipeline/` - Pipeline orchestration
  - `analysis/` - Result analysis and reporting
- `scripts/` - Executable scripts
- `results/` - API results storage
- `tests/` - Unit and integration tests