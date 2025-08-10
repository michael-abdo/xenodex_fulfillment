"""Behavioral Signals API client using shared services"""
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any
import time
import os

# Import shared services protocol
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from xenodx_fulfillment.shared.models import APIClient


class BehavioralSignalsClient(APIClient):
    """Client for Behavioral Signals API implementing shared services protocol"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize client with configuration"""
        # Extract API configuration
        api_config = config.get('api', {})
        self.api_key = api_config.get('key', os.environ.get('BEHAVIORAL_SIGNALS_API_KEY', ''))
        self.client_id = api_config.get('client_id', '10000127')
        self.base_url = api_config.get('base_url', 'https://api.behavioralsignals.com')
        
        # Extract timeout configuration
        timeouts = config.get('timeouts', {})
        self.upload_timeout = timeouts.get('api_submission', 120)
        self.check_interval = timeouts.get('api_check_interval', 5)
        self.max_wait = timeouts.get('max_wait', 600)
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Send file to Behavioral Signals API and wait for results
        
        Args:
            file_path: Path to audio/video file
            
        Returns:
            Dict containing the complete analysis results
        """
        # Submit file for processing
        process_id = await self._submit_file(file_path)
        
        # Monitor until complete
        await self._wait_for_completion(process_id)
        
        # Retrieve and return results
        return await self._get_results(process_id)
    
    async def _submit_file(self, file_path: Path) -> str:
        """Submit file and return process ID"""
        url = f"{self.base_url}/v5/clients/{self.client_id}/processes/audio"
        
        # Determine content type
        ext = file_path.suffix.lower()
        content_type = 'audio/mp3' if ext == '.mp3' else 'video/mp4'
        
        async with aiohttp.ClientSession() as session:
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file',
                          open(file_path, 'rb'),
                          filename=file_path.name,
                          content_type=content_type)
            data.add_field('name', file_path.stem)
            data.add_field('embeddings', 'true')
            
            headers = {'X-Auth-Token': self.api_key}
            
            async with session.post(url, data=data, headers=headers, 
                                  timeout=aiohttp.ClientTimeout(total=self.upload_timeout)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API submission failed with status {response.status}: {error_text}")
                
                result = await response.json()
                process_id = result.get('pid')
                if not process_id:
                    raise Exception(f"No process ID in response: {result}")
                
                return process_id
    
    async def _wait_for_completion(self, process_id: str):
        """Wait for processing to complete"""
        url = f"{self.base_url}/v5/clients/{self.client_id}/processes/{process_id}"
        headers = {
            'X-Auth-Token': self.api_key,
            'accept': 'application/json'
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            while True:
                # Check if timeout exceeded
                if time.time() - start_time > self.max_wait:
                    raise Exception(f"Processing timeout after {self.max_wait} seconds")
                
                # Check status
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"Status check failed with status {response.status}")
                    
                    result = await response.json()
                    status = result.get('status')
                    
                    # Status codes: 0=pending, 1=processing, 2=complete, negative=error
                    if status == 2:  # Complete
                        return
                    elif status < 0:  # Error
                        status_msg = result.get('statusmsg', 'Unknown error')
                        raise Exception(f"Processing failed: {status_msg}")
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
    
    async def _get_results(self, process_id: str) -> Dict[str, Any]:
        """Retrieve processing results"""
        url = f"{self.base_url}/v5/clients/{self.client_id}/processes/{process_id}/results"
        headers = {
            'X-Auth-Token': self.api_key,
            'accept': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get results with status {response.status}")
                
                results = await response.json()
                
                # Return the raw results with additional metadata
                return {
                    'process_id': process_id,
                    'results': results,
                    'file_path': str(file_path),
                    'api_name': 'Behavioral Signals'
                }