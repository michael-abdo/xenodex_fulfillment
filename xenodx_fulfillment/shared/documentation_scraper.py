"""Shared documentation scraping utility for API documentation sites"""
import time
import logging
from pathlib import Path
from typing import Set, Optional
from urllib.parse import urljoin, urlparse


class DocumentationScraper:
    """Generic documentation scraper for API documentation sites"""
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize scraper
        
        Args:
            delay: Delay between requests in seconds
        """
        self.delay = delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.visited_urls: Set[str] = set()
    
    def scrape_documentation_site(
        self,
        start_url: str,
        output_dir: Path,
        max_pages: int = 50,
        base_domain: Optional[str] = None
    ):
        """
        Scrape documentation site starting from URL
        
        Args:
            start_url: Starting URL to scrape
            output_dir: Directory to save scraped content
            max_pages: Maximum number of pages to scrape
            base_domain: Restrict scraping to this domain
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            import html2text
        except ImportError:
            self.logger.error("Required packages not installed. Run: pip install beautifulsoup4 html2text")
            return
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up HTML to Markdown converter
        h2t = html2text.HTML2Text()
        h2t.ignore_links = False
        h2t.ignore_images = False
        h2t.body_width = 0  # Don't wrap lines
        
        # Queue of URLs to process
        urls_to_visit = [start_url]
        
        # Extract base domain if not provided
        if not base_domain:
            parsed = urlparse(start_url)
            base_domain = parsed.netloc
        
        while urls_to_visit and len(self.visited_urls) < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            # Check if URL is within allowed domain
            if urlparse(url).netloc != base_domain:
                continue
            
            try:
                self.logger.info(f"Scraping: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Mark as visited
                self.visited_urls.add(url)
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                page_title = title.text.strip() if title else 'Untitled'
                
                # Convert to markdown
                markdown_content = h2t.handle(response.text)
                
                # Save to file
                # Create filename from URL path
                parsed_url = urlparse(url)
                path_parts = [p for p in parsed_url.path.split('/') if p]
                if not path_parts:
                    path_parts = ['index']
                
                filename = '_'.join(path_parts[-2:]) if len(path_parts) > 1 else path_parts[0]
                filename = filename.replace('.html', '') + '.md'
                
                output_file = output_dir / filename
                output_file.write_text(f"# {page_title}\n\nSource: {url}\n\n{markdown_content}")
                
                # Extract links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    
                    # Add to queue if not visited and same domain
                    if (absolute_url not in self.visited_urls and 
                        absolute_url not in urls_to_visit and
                        urlparse(absolute_url).netloc == base_domain):
                        urls_to_visit.append(absolute_url)
                
                # Respect rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        self.logger.info(f"Scraping complete. Scraped {len(self.visited_urls)} pages")
        self.logger.info(f"Documentation saved to: {output_dir}")
    
    def scrape_api_reference(self, api_docs_url: str, output_file: Path):
        """
        Scrape a single API reference page
        
        Args:
            api_docs_url: URL of API documentation
            output_file: Output file path
        """
        try:
            import requests
            import html2text
        except ImportError:
            self.logger.error("Required packages not installed. Run: pip install beautifulsoup4 html2text")
            return
        
        try:
            self.logger.info(f"Fetching: {api_docs_url}")
            response = requests.get(api_docs_url, timeout=30)
            response.raise_for_status()
            
            # Convert to markdown
            h2t = html2text.HTML2Text()
            h2t.ignore_links = False
            h2t.body_width = 0
            
            markdown_content = h2t.handle(response.text)
            
            # Save
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(f"# API Documentation\n\nSource: {api_docs_url}\n\n{markdown_content}")
            
            self.logger.info(f"Documentation saved to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error fetching documentation: {str(e)}")