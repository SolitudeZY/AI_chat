import httpx
from bs4 import BeautifulSoup
import re

class WebService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def extract_urls(self, text: str) -> list[str]:
        """Extract URLs from text, excluding local uploads."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        # Filter out local uploads
        return [url for url in urls if "localhost" not in url and "/uploads/" not in url]

    async def fetch_content(self, url: str) -> str:
        """Fetch and parse text content from a URL."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading/trailing space on each
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Truncate if too long (to avoid token limits)
                if len(text) > 10000:
                    text = text[:10000] + "...(truncated)"
                    
                return f"URL: {url}\nContent:\n{text}\n"
                
        except Exception as e:
            return f"Error fetching {url}: {str(e)}\n"

web_service = WebService()
