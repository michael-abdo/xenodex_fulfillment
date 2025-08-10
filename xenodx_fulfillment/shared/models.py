"""Shared data models and protocols for all API integrations"""
from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class EmotionCategory(Enum):
    """Standard emotion categories across all APIs"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


@dataclass
class EmotionScore:
    """Emotion score with confidence"""
    category: EmotionCategory
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'category': self.category.value,
            'score': self.score,
            'confidence': self.confidence
        }


@dataclass
class Metadata:
    """Analysis metadata"""
    file_path: str
    api_name: str
    timestamp: datetime = None
    duration: Optional[float] = None  # seconds
    processing_time: Optional[float] = None  # seconds
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'file_path': self.file_path,
            'api_name': self.api_name,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'processing_time': self.processing_time
        }


@dataclass
class AnalysisResult:
    """Standardized analysis result from any API"""
    emotions: List[EmotionScore]
    raw_response: Dict[str, Any]
    metadata: Metadata
    summary: Optional[str] = None
    
    def get_primary_emotion(self) -> Optional[EmotionScore]:
        """Get the emotion with highest score"""
        if not self.emotions:
            return None
        return max(self.emotions, key=lambda e: e.score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'emotions': [e.to_dict() for e in self.emotions],
            'raw_response': self.raw_response,
            'metadata': self.metadata.to_dict(),
            'summary': self.summary
        }


class APIClient(Protocol):
    """Protocol for API client implementations"""
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Send file to API for analysis
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Raw API response as dictionary
        """
        ...


class ResultAnalyzer(Protocol):
    """Protocol for result analyzer implementations"""
    
    def analyze(self, raw_result: Dict[str, Any]) -> AnalysisResult:
        """
        Convert raw API result to standardized AnalysisResult
        
        Args:
            raw_result: Raw response from API
            
        Returns:
            Standardized AnalysisResult
        """
        ...