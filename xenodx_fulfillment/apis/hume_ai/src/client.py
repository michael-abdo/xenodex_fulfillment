"""Hume AI client using shared services"""
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any
import os

# Import shared services protocol
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from xenodx_fulfillment.shared.models import APIClient


class HumeAIClient(APIClient):
    """Client for Hume AI implementing shared services protocol"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize client with configuration"""
        # Extract API configuration
        api_config = config.get('api', {})
        self.api_key = api_config.get('key', os.environ.get('HUME_API_KEY', ''))
        self.base_url = api_config.get('base_url', 'https://api.hume.ai/v0')
        
        # Extract timeout configuration
        timeouts = config.get('timeouts', {})
        self.upload_timeout = timeouts.get('api_submission', 120)
        self.check_interval = timeouts.get('api_check_interval', 5)
        self.max_wait = timeouts.get('max_wait', 600)
        
        if not self.api_key:
            raise ValueError("Hume API key not found. Set HUME_API_KEY environment variable or configure in YAML.")
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Send file to Hume AI and get emotion analysis results
        
        Args:
            file_path: Path to audio/video file
            
        Returns:
            Dict containing the complete analysis results
        """
        # Start analysis job
        job_id = await self._submit_file(file_path)
        
        # Wait for completion
        await self._wait_for_completion(job_id)
        
        # Get and return results
        return await self._get_results(job_id, file_path)
    
    async def _submit_file(self, file_path: Path) -> str:
        """Submit file and return job ID"""
        url = f"{self.base_url}/batch/jobs"
        
        async with aiohttp.ClientSession() as session:
            # Create form data
            data = aiohttp.FormData()
            data.add_field('file',
                          open(file_path, 'rb'),
                          filename=file_path.name,
                          content_type='audio/mpeg')
            
            # Configuration for analysis
            config = {
                "language": {"granularity": "utterance"},
                "prosody": {"granularity": "utterance"}
            }
            data.add_field('json', str(config))
            
            headers = {'X-Hume-Api-Key': self.api_key}
            
            async with session.post(url, data=data, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=self.upload_timeout)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Hume AI submission failed with status {response.status}: {error_text}")
                
                result = await response.json()
                job_id = result.get('job_id')
                if not job_id:
                    raise Exception(f"No job ID in response: {result}")
                
                return job_id
    
    async def _wait_for_completion(self, job_id: str):
        """Wait for job to complete"""
        url = f"{self.base_url}/batch/jobs/{job_id}"
        headers = {'X-Hume-Api-Key': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"Status check failed with status {response.status}")
                    
                    result = await response.json()
                    state = result.get('state', {})
                    status = state.get('status')
                    
                    if status == 'COMPLETED':
                        return
                    elif status in ['FAILED', 'ERROR']:
                        message = state.get('message', 'Unknown error')
                        raise Exception(f"Hume AI processing failed: {message}")
                    elif status not in ['QUEUED', 'IN_PROGRESS']:
                        raise Exception(f"Unknown status: {status}")
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
    
    async def _get_results(self, job_id: str, file_path: Path) -> Dict[str, Any]:
        """Get job results"""
        url = f"{self.base_url}/batch/jobs/{job_id}/predictions"
        headers = {'X-Hume-Api-Key': self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get results with status {response.status}")
                
                predictions = await response.json()
                
                # Return formatted results
                return {
                    'job_id': job_id,
                    'results': {
                        'predictions': predictions
                    },
                    'file_path': str(file_path),
                    'api_name': 'Hume AI'
                }