"""
Crawler and Extractor Modules for Omniscience Engine
Cleans, normalizes, and extracts high-density text snippets from web sources.
Strips raw HTML boilerplate, navigation noise, and web layout junk.
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("sera.omniscience.crawler")

# Keywords that indicate raw web page navigation boilerplate or scraped HTML noise
BOILERPLATE_PATTERNS = [
    r'!DOCTYPE', r'Skip to content', r'Jump to', r'Type \? for help',
    r'Unstar this repository', r'You signed in with another tab', r'Sign out',
    r'Search for issues', r'Pull requests', r'Terms Privacy Security Status',
    r'Edit status', r'Working from home', r'Overview Repositories', r'Clear status'
]

class PageCrawler:
    @classmethod
    async def crawl_and_clean(cls, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_items = []
        for item in raw_items:
            text = item.get("snippet", "")
            clean_text = ContentExtractor.clean_html(text, item.get("title", ""))
            
            cleaned_item = dict(item)
            cleaned_item["clean_text"] = clean_text
            cleaned_item["snippet"] = clean_text
            cleaned_items.append(cleaned_item)
            
        return cleaned_items

class ContentExtractor:
    @classmethod
    def clean_html(cls, text: str, title: str = "") -> str:
        if not text:
            return ""
            
        # Check if text contains raw web boilerplate noise
        for pattern in BOILERPLATE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"[CRAWLER] Boilerplate pattern '{pattern}' detected. Sanitizing snippet.")
                # Replace boilerplate text with clean human summary
                clean_entity = title.replace("GitHub Repo:", "").replace("arXiv Paper:", "").replace("Wikipedia:", "").strip()
                return f"Official open source code repository, documentation, and development artifacts for {clean_entity or 'target entity'}."

        # Remove HTML tags if present
        clean = re.sub(r'<[^>]+>', '', text)
        # Remove excessive whitespace & newlines
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Limit snippet length to 220 characters max for clean UI cards
        if len(clean) > 220:
            clean = clean[:217] + "..."
            
        return clean
