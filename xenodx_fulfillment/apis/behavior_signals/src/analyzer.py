"""Behavioral Signals result analyzer using shared services"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from collections import Counter

# Import shared services
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from xenodx_fulfillment.shared.models import ResultAnalyzer, AnalysisResult, EmotionScore, EmotionCategory, Metadata


class BehavioralSignalsAnalyzer(ResultAnalyzer):
    """Analyzer for Behavioral Signals API results"""
    
    # Map Behavioral Signals emotions to standard categories
    EMOTION_MAP = {
        'neutral': EmotionCategory.NEUTRAL,
        'joy': EmotionCategory.JOY,
        'happy': EmotionCategory.JOY,
        'happiness': EmotionCategory.JOY,
        'sadness': EmotionCategory.SADNESS,
        'sad': EmotionCategory.SADNESS,
        'anger': EmotionCategory.ANGER,
        'angry': EmotionCategory.ANGER,
        'fear': EmotionCategory.FEAR,
        'fearful': EmotionCategory.FEAR,
        'surprise': EmotionCategory.SURPRISE,
        'surprised': EmotionCategory.SURPRISE,
        'disgust': EmotionCategory.DISGUST,
        'disgusted': EmotionCategory.DISGUST,
        'calm': EmotionCategory.NEUTRAL,
        'unknown': EmotionCategory.UNKNOWN
    }
    
    def analyze(self, raw_result: Dict[str, Any]) -> AnalysisResult:
        """
        Convert Behavioral Signals raw results to standardized AnalysisResult
        
        Args:
            raw_result: Raw response from Behavioral Signals API
            
        Returns:
            Standardized AnalysisResult
        """
        # Extract results array
        results_data = raw_result.get('results', [])
        
        # Extract emotion scores
        emotions = self._extract_emotions(results_data)
        
        # Calculate processing metadata
        metadata = self._extract_metadata(raw_result, results_data)
        
        # Generate summary
        summary = self._generate_summary(results_data)
        
        return AnalysisResult(
            emotions=emotions,
            raw_response=raw_result,
            metadata=metadata,
            summary=summary
        )
    
    def _extract_emotions(self, results_data: List[Dict[str, Any]]) -> List[EmotionScore]:
        """Extract emotion scores from results"""
        emotion_scores = []
        
        # Find emotion records in results
        emotion_records = [r for r in results_data if r.get('task') == 'emotion']
        
        if not emotion_records:
            # If no emotions found, return neutral
            return [EmotionScore(
                category=EmotionCategory.NEUTRAL,
                score=1.0,
                confidence=0.5
            )]
        
        # Count occurrences of each emotion
        emotion_counts = Counter()
        total_records = len(emotion_records)
        
        for record in emotion_records:
            emotion_label = record.get('finalLabel', '').lower()
            emotion_counts[emotion_label] += 1
        
        # Convert counts to scores
        for emotion_label, count in emotion_counts.items():
            # Map to standard category
            category = self.EMOTION_MAP.get(emotion_label, EmotionCategory.UNKNOWN)
            
            # Calculate score as percentage of utterances with this emotion
            score = count / total_records
            
            # Extract confidence from predictions if available
            confidence = self._extract_confidence(emotion_records, emotion_label)
            
            emotion_scores.append(EmotionScore(
                category=category,
                score=score,
                confidence=confidence
            ))
        
        # Sort by score descending
        emotion_scores.sort(key=lambda x: x.score, reverse=True)
        
        return emotion_scores
    
    def _extract_confidence(self, emotion_records: List[Dict[str, Any]], emotion_label: str) -> float:
        """Extract average confidence for a specific emotion"""
        confidences = []
        
        for record in emotion_records:
            if record.get('finalLabel', '').lower() == emotion_label:
                predictions = record.get('prediction', [])
                for pred in predictions:
                    if pred.get('label', '').lower() == emotion_label:
                        posterior = pred.get('posterior', 0)
                        if posterior > 0:
                            confidences.append(float(posterior))
        
        return sum(confidences) / len(confidences) if confidences else 0.7
    
    def _extract_metadata(self, raw_result: Dict[str, Any], results_data: List[Dict[str, Any]]) -> Metadata:
        """Extract metadata from results"""
        # Calculate total duration from ASR records
        duration = None
        asr_records = [r for r in results_data if r.get('task') == 'asr']
        if asr_records:
            # Find max end time
            max_end_time = max(float(r.get('endTime', 0)) for r in asr_records)
            if max_end_time > 0:
                duration = max_end_time
        
        # Extract file path
        file_path = raw_result.get('file_path', '')
        
        # Calculate processing time (if start/end timestamps available)
        processing_time = None
        
        return Metadata(
            file_path=file_path,
            duration=duration,
            api_name="Behavioral Signals",
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    def _generate_summary(self, results_data: List[Dict[str, Any]]) -> str:
        """Generate a summary of the analysis"""
        summary_parts = []
        
        # Count speakers
        speaker_records = [r for r in results_data if r.get('task') == 'diarization']
        unique_speakers = set(r.get('finalLabel') for r in speaker_records if r.get('finalLabel'))
        if unique_speakers:
            summary_parts.append(f"{len(unique_speakers)} speaker(s) detected")
        
        # Dominant emotion
        emotion_records = [r for r in results_data if r.get('task') == 'emotion']
        if emotion_records:
            emotion_counts = Counter(r.get('finalLabel', '').lower() for r in emotion_records)
            if emotion_counts:
                dominant_emotion, count = emotion_counts.most_common(1)[0]
                percentage = (count / len(emotion_records)) * 100
                summary_parts.append(f"Primary emotion: {dominant_emotion} ({percentage:.0f}%)")
        
        # Positivity analysis
        positivity_records = [r for r in results_data if r.get('task') == 'positivity']
        if positivity_records:
            positivity_counts = Counter(r.get('finalLabel', '') for r in positivity_records)
            if positivity_counts:
                dominant_sentiment, count = positivity_counts.most_common(1)[0]
                percentage = (count / len(positivity_records)) * 100
                summary_parts.append(f"Overall sentiment: {dominant_sentiment} ({percentage:.0f}%)")
        
        # Engagement level
        engagement_records = [r for r in results_data if r.get('task') == 'engagement']
        if engagement_records:
            engagement_counts = Counter(r.get('finalLabel', '') for r in engagement_records)
            if engagement_counts:
                dominant_engagement, count = engagement_counts.most_common(1)[0]
                percentage = (count / len(engagement_records)) * 100
                summary_parts.append(f"Engagement: {dominant_engagement} ({percentage:.0f}%)")
        
        # Gender detection
        gender_records = [r for r in results_data if r.get('task') == 'gender']
        if gender_records:
            gender_counts = Counter(r.get('finalLabel', '') for r in gender_records)
            if gender_counts:
                genders = [f"{count} {gender}" for gender, count in gender_counts.items()]
                summary_parts.append(f"Gender: {', '.join(genders)}")
        
        # Language detection
        language_records = [r for r in results_data if r.get('task') == 'language']
        if language_records and language_records[0].get('finalLabel'):
            language = language_records[0].get('finalLabel', '').upper()
            summary_parts.append(f"Language: {language}")
        
        return " | ".join(summary_parts) if summary_parts else "Analysis complete"