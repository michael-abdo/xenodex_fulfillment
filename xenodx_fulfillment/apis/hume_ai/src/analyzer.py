"""Hume AI result analyzer using shared services"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Import shared services
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from xenodx_fulfillment.shared.models import ResultAnalyzer, AnalysisResult, EmotionScore, EmotionCategory, Metadata


class HumeAIAnalyzer(ResultAnalyzer):
    """Analyzer for Hume AI results"""
    
    # Map Hume AI emotions to standard categories
    EMOTION_MAP = {
        'Joy': EmotionCategory.JOY,
        'Happiness': EmotionCategory.JOY,
        'Amusement': EmotionCategory.JOY,
        'Excitement': EmotionCategory.JOY,
        'Satisfaction': EmotionCategory.JOY,
        'Relief': EmotionCategory.JOY,
        
        'Sadness': EmotionCategory.SADNESS,
        'Disappointment': EmotionCategory.SADNESS,
        'Grief': EmotionCategory.SADNESS,
        'Sorrow': EmotionCategory.SADNESS,
        
        'Anger': EmotionCategory.ANGER,
        'Rage': EmotionCategory.ANGER,
        'Annoyance': EmotionCategory.ANGER,
        'Irritation': EmotionCategory.ANGER,
        'Frustration': EmotionCategory.ANGER,
        
        'Fear': EmotionCategory.FEAR,
        'Anxiety': EmotionCategory.FEAR,
        'Worry': EmotionCategory.FEAR,
        'Nervousness': EmotionCategory.FEAR,
        'Panic': EmotionCategory.FEAR,
        
        'Surprise': EmotionCategory.SURPRISE,
        'Shock': EmotionCategory.SURPRISE,
        'Amazement': EmotionCategory.SURPRISE,
        
        'Disgust': EmotionCategory.DISGUST,
        'Contempt': EmotionCategory.DISGUST,
        'Repulsion': EmotionCategory.DISGUST,
        
        'Neutral': EmotionCategory.NEUTRAL,
        'Calm': EmotionCategory.NEUTRAL,
        'Serenity': EmotionCategory.NEUTRAL,
        'Contentment': EmotionCategory.NEUTRAL,
        
        # Default for unmapped emotions
        'Unknown': EmotionCategory.UNKNOWN
    }
    
    def analyze(self, raw_result: Dict[str, Any]) -> AnalysisResult:
        """
        Convert Hume AI raw results to standardized AnalysisResult
        
        Args:
            raw_result: Raw response from Hume AI API
            
        Returns:
            Standardized AnalysisResult
        """
        # Extract predictions from nested structure
        results = raw_result.get('results', {})
        predictions = results.get('predictions', [])
        
        # Extract emotion scores
        emotions = self._extract_emotions(predictions)
        
        # Calculate metadata
        metadata = self._extract_metadata(raw_result, predictions)
        
        # Generate summary
        summary = self._generate_summary(predictions)
        
        return AnalysisResult(
            emotions=emotions,
            raw_response=raw_result,
            metadata=metadata,
            summary=summary
        )
    
    def _extract_emotions(self, predictions: List[Dict[str, Any]]) -> List[EmotionScore]:
        """Extract emotion scores from Hume AI predictions"""
        emotion_scores = {}
        
        # Process all predictions
        for prediction in predictions:
            models = prediction.get('models', {})
            
            # Check language model for speech-based emotions
            if 'language' in models:
                lang_predictions = models['language'].get('predictions', [])
                for pred in lang_predictions:
                    emotions = pred.get('emotions', [])
                    self._accumulate_emotions(emotions, emotion_scores)
            
            # Check prosody model for speech patterns
            if 'prosody' in models:
                prosody_predictions = models['prosody'].get('predictions', [])
                for pred in prosody_predictions:
                    emotions = pred.get('emotions', [])
                    self._accumulate_emotions(emotions, emotion_scores)
        
        # Convert accumulated scores to EmotionScore objects
        result_emotions = []
        
        if not emotion_scores:
            # Return neutral if no emotions found
            return [EmotionScore(
                category=EmotionCategory.NEUTRAL,
                score=1.0,
                confidence=0.5
            )]
        
        # Calculate total score for normalization
        total_score = sum(data['total_score'] for data in emotion_scores.values())
        
        for emotion_name, data in emotion_scores.items():
            # Map to standard category
            category = self.EMOTION_MAP.get(emotion_name, EmotionCategory.UNKNOWN)
            
            # Normalize score
            normalized_score = data['total_score'] / total_score if total_score > 0 else 0
            
            # Calculate average confidence
            avg_confidence = data['total_confidence'] / data['count'] if data['count'] > 0 else 0
            
            result_emotions.append(EmotionScore(
                category=category,
                score=normalized_score,
                confidence=avg_confidence
            ))
        
        # Sort by score descending
        result_emotions.sort(key=lambda x: x.score, reverse=True)
        
        return result_emotions
    
    def _accumulate_emotions(self, emotions: List[Dict[str, Any]], emotion_scores: Dict[str, Dict]):
        """Accumulate emotion scores from a list of emotions"""
        for emotion in emotions:
            name = emotion.get('name', 'Unknown')
            score = emotion.get('score', 0)
            
            if name not in emotion_scores:
                emotion_scores[name] = {
                    'total_score': 0,
                    'total_confidence': 0,
                    'count': 0
                }
            
            emotion_scores[name]['total_score'] += score
            emotion_scores[name]['total_confidence'] += score  # Use score as confidence
            emotion_scores[name]['count'] += 1
    
    def _extract_metadata(self, raw_result: Dict[str, Any], predictions: List[Dict[str, Any]]) -> Metadata:
        """Extract metadata from Hume AI results"""
        # Extract file path
        file_path = raw_result.get('file_path', '')
        
        # Calculate duration from predictions if available
        duration = None
        if predictions:
            # Look for time-based data in predictions
            for prediction in predictions:
                models = prediction.get('models', {})
                for model_name, model_data in models.items():
                    preds = model_data.get('predictions', [])
                    for pred in preds:
                        # Try to find time information
                        time_info = pred.get('time')
                        if time_info:
                            end = time_info.get('end')
                            if end and (duration is None or end > duration):
                                duration = end
        
        return Metadata(
            file_path=file_path,
            duration=duration,
            api_name="Hume AI",
            processing_time=None,  # Not available from Hume AI response
            timestamp=datetime.now()
        )
    
    def _generate_summary(self, predictions: List[Dict[str, Any]]) -> str:
        """Generate a summary of the Hume AI analysis"""
        summary_parts = []
        
        if not predictions:
            return "No analysis results available"
        
        # Count models used
        models_used = set()
        total_predictions = 0
        
        for prediction in predictions:
            models = prediction.get('models', {})
            models_used.update(models.keys())
            
            for model_name, model_data in models.items():
                preds = model_data.get('predictions', [])
                total_predictions += len(preds)
        
        if models_used:
            summary_parts.append(f"Analysis using {', '.join(models_used)} models")
        
        if total_predictions > 0:
            summary_parts.append(f"{total_predictions} prediction(s) generated")
        
        # Try to identify dominant emotions
        emotion_counts = {}
        for prediction in predictions:
            models = prediction.get('models', {})
            for model_name, model_data in models.items():
                preds = model_data.get('predictions', [])
                for pred in preds:
                    emotions = pred.get('emotions', [])
                    if emotions:
                        # Get top emotion
                        top_emotion = max(emotions, key=lambda e: e.get('score', 0))
                        emotion_name = top_emotion.get('name', 'Unknown')
                        emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
        
        if emotion_counts:
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
            summary_parts.append(f"Dominant emotion: {dominant_emotion[0]}")
        
        return " | ".join(summary_parts) if summary_parts else "Hume AI analysis complete"