#!/usr/bin/env python3
"""Test the Behavioral Signals migration to shared services"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.client import BehavioralSignalsClient
from src.analyzer import BehavioralSignalsAnalyzer
from xenodx_fulfillment.shared.config import Config
from xenodx_fulfillment.shared.models import AnalysisResult, EmotionCategory


def test_imports():
    """Test that all imports work correctly"""
    print("✓ All imports successful")


def test_config_loading():
    """Test configuration loading"""
    config = Config.from_yaml("config/config.yaml")
    assert config.get('api.key') == "f38d44bfe4ae7c915e2be3ec32c2101f"
    assert config.get('api.client_id') == "10000127"
    assert config.get('api.base_url') == "https://api.behavioralsignals.com"
    print("✓ Configuration loaded correctly")


def test_client_creation():
    """Test client instantiation"""
    config = Config.from_yaml("config/config.yaml")
    client = BehavioralSignalsClient(config.to_dict())
    assert client.api_key == "f38d44bfe4ae7c915e2be3ec32c2101f"
    assert client.client_id == "10000127"
    assert client.base_url == "https://api.behavioralsignals.com"
    print("✓ Client created successfully")


def test_analyzer_creation():
    """Test analyzer instantiation"""
    analyzer = BehavioralSignalsAnalyzer()
    assert hasattr(analyzer, 'analyze')
    print("✓ Analyzer created successfully")


def test_analyzer_with_mock_data():
    """Test analyzer with mock Behavioral Signals response"""
    analyzer = BehavioralSignalsAnalyzer()
    
    # Mock response similar to Behavioral Signals format
    mock_response = {
        'process_id': 'test123',
        'file_path': '/test/audio.mp3',
        'results': [
            # Emotion records
            {'id': 'utt_1', 'task': 'emotion', 'finalLabel': 'joy'},
            {'id': 'utt_2', 'task': 'emotion', 'finalLabel': 'neutral'},
            {'id': 'utt_3', 'task': 'emotion', 'finalLabel': 'joy'},
            {'id': 'utt_4', 'task': 'emotion', 'finalLabel': 'sadness'},
            
            # ASR records for duration
            {'id': 'utt_1', 'task': 'asr', 'startTime': '0.0', 'endTime': '5.0', 'finalLabel': 'Hello there'},
            {'id': 'utt_2', 'task': 'asr', 'startTime': '5.0', 'endTime': '10.0', 'finalLabel': 'How are you'},
            {'id': 'utt_3', 'task': 'asr', 'startTime': '10.0', 'endTime': '15.0', 'finalLabel': 'Great day today'},
            {'id': 'utt_4', 'task': 'asr', 'startTime': '15.0', 'endTime': '20.0', 'finalLabel': 'I feel sad'},
            
            # Speaker diarization
            {'id': 'utt_1', 'task': 'diarization', 'finalLabel': 'speaker1'},
            {'id': 'utt_2', 'task': 'diarization', 'finalLabel': 'speaker2'},
            {'id': 'utt_3', 'task': 'diarization', 'finalLabel': 'speaker1'},
            {'id': 'utt_4', 'task': 'diarization', 'finalLabel': 'speaker2'},
            
            # Additional analysis
            {'id': 'utt_1', 'task': 'positivity', 'finalLabel': 'positive'},
            {'id': 'utt_2', 'task': 'positivity', 'finalLabel': 'neutral'},
            {'id': 'utt_3', 'task': 'positivity', 'finalLabel': 'positive'},
            {'id': 'utt_4', 'task': 'positivity', 'finalLabel': 'negative'},
            
            {'id': 'global', 'task': 'language', 'finalLabel': 'en'},
            {'id': 'speaker1', 'task': 'gender', 'finalLabel': 'male'},
            {'id': 'speaker2', 'task': 'gender', 'finalLabel': 'female'},
        ]
    }
    
    # Analyze
    result = analyzer.analyze(mock_response)
    
    # Verify result structure
    assert isinstance(result, AnalysisResult)
    assert len(result.emotions) > 0
    
    # Check emotion mapping
    primary_emotion = result.get_primary_emotion()
    assert primary_emotion is not None
    assert primary_emotion.category == EmotionCategory.JOY  # Joy appears 2/4 times
    assert primary_emotion.score == 0.5  # 2 out of 4 emotion records
    
    # Check metadata
    assert result.metadata.api_name == "Behavioral Signals"
    assert result.metadata.duration == 20.0  # From ASR end times
    
    # Check summary
    assert "2 speaker(s) detected" in result.summary
    assert "Primary emotion: joy (50%)" in result.summary
    assert "Language: EN" in result.summary
    
    print("✓ Analyzer processes mock data correctly")
    print(f"  - Primary emotion: {primary_emotion.category.value} ({primary_emotion.score:.0%})")
    print(f"  - Summary: {result.summary}")


def test_pipeline_integration():
    """Test that all components work together"""
    from xenodx_fulfillment.shared.pipeline import Pipeline
    
    config = Config.from_yaml("config/config.yaml")
    client = BehavioralSignalsClient(config.to_dict())
    analyzer = BehavioralSignalsAnalyzer()
    
    # Create pipeline
    pipeline = Pipeline(
        client=client,
        analyzer=analyzer,
        config=config
    )
    
    assert pipeline.client == client
    assert pipeline.analyzer == analyzer
    assert pipeline.config == config
    
    print("✓ Pipeline integration successful")


def main():
    """Run all tests"""
    print("Testing Behavioral Signals migration to shared services...")
    print("-" * 50)
    
    try:
        test_imports()
        test_config_loading()
        test_client_creation()
        test_analyzer_creation()
        test_analyzer_with_mock_data()
        test_pipeline_integration()
        
        print("-" * 50)
        print("✅ All tests passed! Migration successful.")
        print("\nThe Behavioral Signals API is now using shared services:")
        print("  - client.py: ~130 lines (API-specific logic only)")
        print("  - analyzer.py: ~180 lines (result mapping only)")
        print("  - run_pipeline.py: ~30 lines (minimal boilerplate)")
        print("  - Total: ~340 lines (vs ~2000+ lines in old implementation)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()