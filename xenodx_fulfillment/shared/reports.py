"""Shared report generation for all API integrations"""
import json
from pathlib import Path
from typing import Dict, Any

from .models import AnalysisResult


class ReportGenerator:
    """Generate reports in multiple formats"""
    
    def generate_report(self, result: AnalysisResult, format: str = 'json') -> str:
        """
        Generate report in specified format
        
        Args:
            result: Analysis result
            format: Output format ('json', 'html', 'markdown')
            
        Returns:
            Report content as string
        """
        if format == 'json':
            return self._generate_json(result)
        elif format == 'html':
            return self._generate_html(result)
        elif format == 'markdown':
            return self._generate_markdown(result)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def save_report(self, result: AnalysisResult, output_path: Path, format: str = 'json') -> Path:
        """
        Save report to file
        
        Args:
            result: Analysis result
            output_path: Output file path
            format: Output format
            
        Returns:
            Path to saved file
        """
        content = self.generate_report(result, format)
        output_path.write_text(content)
        return output_path
    
    def _generate_json(self, result: AnalysisResult) -> str:
        """Generate JSON report"""
        return json.dumps(result.to_dict(), indent=2, default=str)
    
    def _generate_html(self, result: AnalysisResult) -> str:
        """Generate HTML report"""
        data = result.to_dict()
        primary = result.get_primary_emotion()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Emotion Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .emotion-bar {{ background-color: #4CAF50; height: 20px; }}
        .metadata {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Emotion Analysis Report</h1>
    
    <div class="metadata">
        <h2>Metadata</h2>
        <p><strong>File:</strong> {data['metadata']['file_path']}</p>
        <p><strong>API:</strong> {data['metadata']['api_name']}</p>
        <p><strong>Timestamp:</strong> {data['metadata']['timestamp']}</p>
        <p><strong>Duration:</strong> {data['metadata']['duration'] or 'N/A'} seconds</p>
        <p><strong>Processing Time:</strong> {data['metadata']['processing_time'] or 'N/A'} seconds</p>
    </div>
    
    <h2>Summary</h2>
    <p>{data['summary'] or 'No summary available'}</p>
    
    <h2>Emotion Scores</h2>
    <table>
        <tr>
            <th>Category</th>
            <th>Score</th>
            <th>Confidence</th>
            <th>Visual</th>
        </tr>
"""
        
        for emotion in data['emotions']:
            score_pct = emotion['score'] * 100
            conf_pct = emotion['confidence'] * 100
            html += f"""
        <tr>
            <td>{emotion['category']}</td>
            <td>{score_pct:.1f}%</td>
            <td>{conf_pct:.1f}%</td>
            <td><div class="emotion-bar" style="width: {score_pct}%"></div></td>
        </tr>
"""
        
        html += """
    </table>
    
"""
        
        if primary:
            html += f"""
    <h2>Primary Emotion</h2>
    <p style="font-size: 24px; font-weight: bold;">
        {primary.category.value.upper()} ({primary.score * 100:.0f}%)
    </p>
"""
        
        html += """
</body>
</html>"""
        
        return html
    
    def _generate_markdown(self, result: AnalysisResult) -> str:
        """Generate Markdown report"""
        data = result.to_dict()
        primary = result.get_primary_emotion()
        
        md = f"""# Emotion Analysis Report

## Summary

{data['summary'] or 'No summary available'}

## Emotion Scores

| Category | Score | Confidence |
|----------|-------|------------|
"""
        
        for emotion in data['emotions']:
            score_pct = emotion['score'] * 100
            conf_pct = emotion['confidence'] * 100
            md += f"| {emotion['category']} | {score_pct:.1f}% | {conf_pct:.1f}% |\n"
        
        if primary:
            md += f"\n## Primary Emotion\n\n**{primary.category.value.upper()}** ({primary.score * 100:.0f}%)\n"
        
        md += f"""
## Metadata

- **File Path:** {data['metadata']['file_path']}
- **API Name:** {data['metadata']['api_name']}
- **Timestamp:** {data['metadata']['timestamp']}
- **Duration:** {data['metadata']['duration'] or 'N/A'} seconds
- **Processing Time:** {data['metadata']['processing_time'] or 'N/A'} seconds
"""
        
        return md