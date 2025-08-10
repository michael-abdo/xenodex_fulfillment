import pytest
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import (
    EmotionCategory, AnalysisResult, EmotionScore, 
    Metadata, APIClient, ResultAnalyzer
)


class TestEmotionCategory:
    def test_emotion_categories(self):
        """Test emotion category enum values"""
        assert EmotionCategory.JOY.value == "joy"
        assert EmotionCategory.SADNESS.value == "sadness"
        assert EmotionCategory.ANGER.value == "anger"
        assert EmotionCategory.FEAR.value == "fear"
        assert EmotionCategory.SURPRISE.value == "surprise"
        assert EmotionCategory.DISGUST.value == "disgust"
        assert EmotionCategory.NEUTRAL.value == "neutral"
        assert EmotionCategory.UNKNOWN.value == "unknown"
    
    def test_emotion_category_from_string(self):
        """Test creating emotion category from string"""
        assert EmotionCategory("joy") == EmotionCategory.JOY
        assert EmotionCategory("neutral") == EmotionCategory.NEUTRAL


class TestEmotionScore:
    def test_emotion_score_creation(self):
        """Test creating emotion score"""
        score = EmotionScore(
            category=EmotionCategory.JOY,
            score=0.85,
            confidence=0.90
        )
        assert score.category == EmotionCategory.JOY
        assert score.score == 0.85
        assert score.confidence == 0.90
    
    def test_emotion_score_to_dict(self):
        """Test converting emotion score to dict"""
        score = EmotionScore(
            category=EmotionCategory.SADNESS,
            score=0.65,
            confidence=0.75
        )
        data = score.to_dict()
        assert data['category'] == 'sadness'
        assert data['score'] == 0.65
        assert data['confidence'] == 0.75


class TestMetadata:
    def test_metadata_creation(self):
        """Test creating metadata"""
        metadata = Metadata(
            file_path="/path/to/file.mp3",
            duration=120.5,
            api_name="Test API",
            processing_time=5.3
        )
        assert metadata.file_path == "/path/to/file.mp3"
        assert metadata.duration == 120.5
        assert metadata.api_name == "Test API"
        assert metadata.processing_time == 5.3
        assert isinstance(metadata.timestamp, datetime)
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dict"""
        metadata = Metadata(
            file_path="/test.mp3",
            api_name="Test"
        )
        data = metadata.to_dict()
        assert data['file_path'] == "/test.mp3"
        assert data['api_name'] == "Test"
        assert 'timestamp' in data
        assert data['duration'] is None
        assert data['processing_time'] is None


class TestAnalysisResult:
    def test_analysis_result_creation(self):
        """Test creating analysis result"""
        emotions = [
            EmotionScore(EmotionCategory.JOY, 0.8, 0.9),
            EmotionScore(EmotionCategory.NEUTRAL, 0.2, 0.7)
        ]
        metadata = Metadata(
            file_path="/test.mp3",
            api_name="Test API"
        )
        
        result = AnalysisResult(
            emotions=emotions,
            raw_response={"test": "data"},
            metadata=metadata,
            summary="Test summary"
        )
        
        assert len(result.emotions) == 2
        assert result.emotions[0].category == EmotionCategory.JOY
        assert result.raw_response == {"test": "data"}
        assert result.metadata.api_name == "Test API"
        assert result.summary == "Test summary"
    
    def test_analysis_result_to_dict(self):
        """Test converting analysis result to dict"""
        emotions = [EmotionScore(EmotionCategory.ANGER, 0.6, 0.8)]
        metadata = Metadata(file_path="/test.mp3", api_name="Test")
        
        result = AnalysisResult(
            emotions=emotions,
            raw_response={"raw": "data"},
            metadata=metadata
        )
        
        data = result.to_dict()
        assert 'emotions' in data
        assert len(data['emotions']) == 1
        assert data['emotions'][0]['category'] == 'anger'
        assert data['raw_response'] == {"raw": "data"}
        assert 'metadata' in data
        assert data['summary'] is None
    
    def test_get_primary_emotion(self):
        """Test getting primary emotion"""
        emotions = [
            EmotionScore(EmotionCategory.JOY, 0.3, 0.9),
            EmotionScore(EmotionCategory.SADNESS, 0.7, 0.8),
            EmotionScore(EmotionCategory.NEUTRAL, 0.1, 0.6)
        ]
        
        result = AnalysisResult(
            emotions=emotions,
            raw_response={},
            metadata=Metadata(file_path="/test.mp3", api_name="Test")
        )
        
        primary = result.get_primary_emotion()
        assert primary is not None
        assert primary.category == EmotionCategory.SADNESS
        assert primary.score == 0.7
    
    def test_get_primary_emotion_empty(self):
        """Test getting primary emotion with no emotions"""
        result = AnalysisResult(
            emotions=[],
            raw_response={},
            metadata=Metadata(file_path="/test.mp3", api_name="Test")
        )
        
        primary = result.get_primary_emotion()
        assert primary is None


class TestProtocols:
    def test_api_client_protocol(self):
        """Test APIClient protocol structure"""
        class TestClient:
            def __init__(self, config):
                pass
            
            async def analyze_file(self, file_path):
                return {"result": "test"}
        
        # Should be able to use as APIClient type
        client = TestClient({})
        assert hasattr(client, 'analyze_file')
    
    def test_result_analyzer_protocol(self):
        """Test ResultAnalyzer protocol structure"""
        class TestAnalyzer:
            def analyze(self, raw_result):
                return AnalysisResult(
                    emotions=[],
                    raw_response=raw_result,
                    metadata=Metadata(file_path="/test", api_name="Test")
                )
        
        # Should be able to use as ResultAnalyzer type
        analyzer = TestAnalyzer()
        assert hasattr(analyzer, 'analyze')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])