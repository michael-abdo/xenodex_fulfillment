import pytest
import tempfile
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.pipeline import Pipeline
from shared.config import Config
from shared.models import AnalysisResult, EmotionScore, EmotionCategory, Metadata


class MockClient:
    """Mock API client for testing"""
    def __init__(self, config):
        self.config = config
        self.analyze_called = False
    
    async def analyze_file(self, file_path):
        self.analyze_called = True
        return {"mock": "response", "status": "success"}


class MockAnalyzer:
    """Mock result analyzer for testing"""
    def __init__(self):
        self.analyze_called = False
    
    def analyze(self, raw_result):
        self.analyze_called = True
        return AnalysisResult(
            emotions=[
                EmotionScore(EmotionCategory.JOY, 0.8, 0.9),
                EmotionScore(EmotionCategory.NEUTRAL, 0.2, 0.7)
            ],
            raw_response=raw_result,
            metadata=Metadata(
                file_path="/test.mp3",
                api_name="Mock API",
                processing_time=1.5
            ),
            summary="Mock analysis complete"
        )


class TestPipeline:
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        return Config(data={
            'api_name': 'Mock API',
            'job_tracking': {
                'enable': True,
                'directory': 'test_jobs'
            },
            'reports': {
                'formats': ['json', 'html'],
                'output_directory': 'test_reports'
            },
            'error_handling': {
                'max_retries': 2,
                'retry_delay': 0.1
            }
        })
    
    @pytest.fixture
    def pipeline(self, mock_config):
        """Create pipeline with mock components"""
        return Pipeline(
            client=MockClient(mock_config.to_dict()),
            analyzer=MockAnalyzer(),
            config=mock_config
        )
    
    @pytest.mark.asyncio
    async def test_process_file_success(self, pipeline):
        """Test successful file processing"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"fake audio")
            f.flush()
            
            result = await pipeline.process_file(Path(f.name))
            
            assert isinstance(result, AnalysisResult)
            assert len(result.emotions) == 2
            assert result.emotions[0].category == EmotionCategory.JOY
            assert pipeline.client.analyze_called
            assert pipeline.analyzer.analyze_called
            
            Path(f.name).unlink()
    
    @pytest.mark.asyncio
    async def test_process_file_with_retries(self, mock_config):
        """Test file processing with retries on failure"""
        # Create a client that fails once then succeeds
        class RetryClient:
            def __init__(self, config):
                self.attempts = 0
            
            async def analyze_file(self, file_path):
                self.attempts += 1
                if self.attempts == 1:
                    raise Exception("Temporary failure")
                return {"status": "success"}
        
        pipeline = Pipeline(
            client=RetryClient(mock_config.to_dict()),
            analyzer=MockAnalyzer(),
            config=mock_config
        )
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"fake audio")
            f.flush()
            
            result = await pipeline.process_file(Path(f.name))
            
            assert isinstance(result, AnalysisResult)
            assert pipeline.client.attempts == 2  # Failed once, succeeded on retry
            
            Path(f.name).unlink()
    
    @pytest.mark.asyncio
    async def test_process_file_max_retries_exceeded(self, mock_config):
        """Test file processing when max retries exceeded"""
        # Create a client that always fails
        class FailingClient:
            async def analyze_file(self, file_path):
                raise Exception("Permanent failure")
        
        pipeline = Pipeline(
            client=FailingClient(),
            analyzer=MockAnalyzer(),
            config=mock_config
        )
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"fake audio")
            f.flush()
            
            with pytest.raises(Exception) as exc_info:
                await pipeline.process_file(Path(f.name))
            
            assert "Permanent failure" in str(exc_info.value)
            
            Path(f.name).unlink()
    
    def test_save_job_info(self, pipeline):
        """Test saving job information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline.config._data['job_tracking']['directory'] = tmpdir
            
            job_info = {
                'job_id': 'test123',
                'status': 'completed',
                'file': '/test.mp3'
            }
            
            pipeline._save_job_info(job_info)
            
            # Check job file was created
            job_files = list(Path(tmpdir).glob('*.json'))
            assert len(job_files) == 1
            
            # Verify content
            with open(job_files[0]) as f:
                saved_info = json.load(f)
                assert saved_info['job_id'] == 'test123'
                assert saved_info['status'] == 'completed'
    
    def test_generate_reports(self, pipeline):
        """Test report generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline.config._data['reports']['output_directory'] = tmpdir
            
            result = AnalysisResult(
                emotions=[EmotionScore(EmotionCategory.JOY, 0.9, 0.95)],
                raw_response={"test": "data"},
                metadata=Metadata(file_path="/test.mp3", api_name="Test"),
                summary="Test summary"
            )
            
            pipeline._generate_reports(result, "test_job_123")
            
            # Check reports were created
            report_files = list(Path(tmpdir).iterdir())
            assert len(report_files) >= 2  # JSON and HTML
            
            # Check JSON report
            json_files = [f for f in report_files if f.suffix == '.json']
            assert len(json_files) == 1
            with open(json_files[0]) as f:
                data = json.load(f)
                assert data['summary'] == "Test summary"
    
    @patch('sys.argv', ['pipeline.py', '/test/file.mp3'])
    def test_run_with_cli_args(self, pipeline):
        """Test running pipeline with command line arguments"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"fake audio")
            f.flush()
            
            with patch('sys.argv', ['pipeline.py', f.name]):
                with patch.object(pipeline, 'process_file', new_callable=AsyncMock) as mock_process:
                    mock_process.return_value = AnalysisResult(
                        emotions=[],
                        raw_response={},
                        metadata=Metadata(file_path=f.name, api_name="Test")
                    )
                    
                    # Run should handle the async execution
                    pipeline.run()
                    
                    mock_process.assert_called_once()
                    call_args = mock_process.call_args[0][0]
                    assert str(call_args) == f.name
            
            Path(f.name).unlink()
    
    def test_run_without_file_argument(self, pipeline):
        """Test running pipeline without file argument"""
        with patch('sys.argv', ['pipeline.py']):
            with pytest.raises(SystemExit):
                pipeline.run()
    
    def test_pipeline_with_disabled_features(self):
        """Test pipeline with job tracking and reports disabled"""
        config = Config(data={
            'api_name': 'Test',
            'job_tracking': {'enable': False},
            'reports': {'formats': []}
        })
        
        pipeline = Pipeline(
            client=MockClient({}),
            analyzer=MockAnalyzer(),
            config=config
        )
        
        # Should not create job files or reports
        with patch.object(pipeline, '_save_job_info') as mock_save:
            with patch.object(pipeline, '_generate_reports') as mock_reports:
                result = AnalysisResult(
                    emotions=[],
                    raw_response={},
                    metadata=Metadata(file_path="/test.mp3", api_name="Test")
                )
                
                # Simulate processing without actual file
                pipeline._handle_result(result, "test_job")
                
                mock_save.assert_not_called()
                mock_reports.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])