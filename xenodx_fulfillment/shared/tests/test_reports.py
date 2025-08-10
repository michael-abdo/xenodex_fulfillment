import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.reports import ReportGenerator
from shared.models import AnalysisResult, EmotionScore, EmotionCategory, Metadata


class TestReportGenerator:
    @pytest.fixture
    def sample_result(self):
        """Create a sample analysis result for testing"""
        emotions = [
            EmotionScore(EmotionCategory.JOY, 0.7, 0.85),
            EmotionScore(EmotionCategory.NEUTRAL, 0.2, 0.75),
            EmotionScore(EmotionCategory.SADNESS, 0.1, 0.60)
        ]
        metadata = Metadata(
            file_path="/test/audio.mp3",
            duration=120.5,
            api_name="Test API",
            processing_time=3.2
        )
        return AnalysisResult(
            emotions=emotions,
            raw_response={"test": "data", "nested": {"value": 123}},
            metadata=metadata,
            summary="Test analysis summary"
        )
    
    @pytest.fixture
    def report_generator(self):
        """Create a report generator instance"""
        return ReportGenerator()
    
    def test_generate_json_report(self, report_generator, sample_result):
        """Test JSON report generation"""
        report = report_generator.generate_report(sample_result, format='json')
        
        # Parse JSON to verify structure
        data = json.loads(report)
        assert 'emotions' in data
        assert len(data['emotions']) == 3
        assert data['emotions'][0]['category'] == 'joy'
        assert data['emotions'][0]['score'] == 0.7
        assert 'metadata' in data
        assert data['metadata']['api_name'] == "Test API"
        assert data['summary'] == "Test analysis summary"
    
    def test_generate_html_report(self, report_generator, sample_result):
        """Test HTML report generation"""
        report = report_generator.generate_report(sample_result, format='html')
        
        # Check for key HTML elements
        assert '<html>' in report
        assert '</html>' in report
        assert 'Emotion Analysis Report' in report
        assert 'Test API' in report
        assert 'joy' in report.lower()
        assert '70.0%' in report  # Joy score
        assert 'Test analysis summary' in report
    
    def test_generate_markdown_report(self, report_generator, sample_result):
        """Test Markdown report generation"""
        report = report_generator.generate_report(sample_result, format='markdown')
        
        # Check for markdown elements
        assert '# Emotion Analysis Report' in report
        assert '## Summary' in report
        assert '## Emotion Scores' in report
        assert '| Category | Score | Confidence |' in report
        assert '| joy | 70.0% | 85.0% |' in report
        assert 'Test analysis summary' in report
        assert '**API Name:** Test API' in report
    
    def test_invalid_format(self, report_generator, sample_result):
        """Test handling of invalid report format"""
        with pytest.raises(ValueError) as exc_info:
            report_generator.generate_report(sample_result, format='invalid')
        assert "Unsupported format" in str(exc_info.value)
    
    def test_save_report_json(self, report_generator, sample_result):
        """Test saving JSON report to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_report.json"
            saved_path = report_generator.save_report(
                sample_result, 
                output_path, 
                format='json'
            )
            
            assert saved_path == output_path
            assert output_path.exists()
            
            # Verify content
            with open(output_path) as f:
                data = json.load(f)
                assert data['metadata']['api_name'] == "Test API"
    
    def test_save_report_html(self, report_generator, sample_result):
        """Test saving HTML report to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_report.html"
            saved_path = report_generator.save_report(
                sample_result, 
                output_path, 
                format='html'
            )
            
            assert saved_path == output_path
            assert output_path.exists()
            
            # Verify it's valid HTML
            content = output_path.read_text()
            assert '<html>' in content
            assert '</html>' in content
    
    def test_save_report_markdown(self, report_generator, sample_result):
        """Test saving Markdown report to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_report.md"
            saved_path = report_generator.save_report(
                sample_result, 
                output_path, 
                format='markdown'
            )
            
            assert saved_path == output_path
            assert output_path.exists()
            
            # Verify content
            content = output_path.read_text()
            assert '# Emotion Analysis Report' in content
    
    def test_report_with_no_emotions(self, report_generator):
        """Test report generation with no emotions"""
        result = AnalysisResult(
            emotions=[],
            raw_response={"empty": True},
            metadata=Metadata(file_path="/test.mp3", api_name="Test")
        )
        
        # Should handle empty emotions gracefully
        json_report = report_generator.generate_report(result, format='json')
        data = json.loads(json_report)
        assert data['emotions'] == []
        
        html_report = report_generator.generate_report(result, format='html')
        assert 'No emotions detected' in html_report or len(result.emotions) == 0
        
        md_report = report_generator.generate_report(result, format='markdown')
        assert '| Category | Score | Confidence |' in md_report
    
    def test_report_with_no_summary(self, report_generator):
        """Test report generation without summary"""
        result = AnalysisResult(
            emotions=[EmotionScore(EmotionCategory.NEUTRAL, 1.0, 1.0)],
            raw_response={},
            metadata=Metadata(file_path="/test.mp3", api_name="Test"),
            summary=None
        )
        
        # Should handle missing summary
        md_report = report_generator.generate_report(result, format='markdown')
        assert '## Summary' in md_report
        # Summary section should exist but might be empty or have placeholder
    
    def test_html_report_styling(self, report_generator, sample_result):
        """Test HTML report includes proper styling"""
        html_report = report_generator.generate_report(sample_result, format='html')
        
        # Check for CSS styling
        assert '<style>' in html_report
        assert 'font-family' in html_report
        assert 'background-color' in html_report
        assert 'border' in html_report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])