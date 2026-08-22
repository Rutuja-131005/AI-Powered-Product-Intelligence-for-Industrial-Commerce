"""
Sources Scraper Module
Fetches content, datasheets, or specs from authoritative sources.
"""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def scrape_url(url: str, timeout: int = 10) -> Optional[str]:
    """Fetches text content from a given URL."""
    try:
        res = requests.get(url, timeout=timeout, headers={"User-Agent": "ProductIntelligenceBot/1.0"})
        if res.status_code == 200:
            return res.text
    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
    return None
