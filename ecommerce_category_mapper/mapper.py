"""Category mapper for ecommerce websites using AI Scraper."""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any, Set
from urllib.parse import urljoin, urlparse
from oxylabs_ai_studio.apps.ai_scraper import AiScraper

from .models import Category, CategoryMap
from .schemas import CATEGORY_SCHEMA

logger = logging.getLogger(__name__)
MIN_CATEGORIES_THRESHOLD_PER_DEPTH = 1
MAX_NO_CATEGORIES_THRESHOLD_PER_DEPTH = 0.7


class RateLimiter:
    """Rate limiter to control request frequency."""
    
    def __init__(self, max_concurrent: int = 5, delay_between_requests: float = 1.0):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay_between_requests
        self.last_request_time = 0
    
    async def acquire(self):
        """Acquire permission to make a request."""
        await self.semaphore.acquire()
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            await asyncio.sleep(self.delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def release(self):
        """Release the semaphore."""
        self.semaphore.release()
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()


class URLTracker:
    """Track visited URLs and exploration statistics."""
    
    def __init__(self):
        self.visited_urls: Set[str] = set()
        self.categories_found_per_url: Dict[str, int] = {}
        self.depth_stats: Dict[int, Dict[str, Any]] = {}
    
    def mark_url_visited(self, url: str):
        """Mark a URL as visited and record categories found."""
        self.visited_urls.add(url)
    
    def get_depth_stats(self, depth: int) -> Dict[str, Any]:
        """Get statistics for a specific depth level."""
        if depth not in self.depth_stats:
            self.depth_stats[depth] = {
                'urls_processed': 0,
                'total_categories_found': 0,
                'urls_with_categories': 0,
                'urls_without_categories': 0
            }
        return self.depth_stats[depth]
    
    def update_depth_stats(self, depth: int, categories_found: int):
        """Update statistics for a depth level."""
        stats = self.get_depth_stats(depth)
        stats['urls_processed'] += 1
        stats['total_categories_found'] += categories_found
        
        if categories_found > 0:
            stats['urls_with_categories'] += 1
        else:
            stats['urls_without_categories'] += 1
    
    def should_stop_exploration_at_depth(self, depth: int) -> bool:
        """Determine if exploration should stop at this depth."""
        stats = self.get_depth_stats(depth)
        
        if stats['urls_processed'] >= 5:
            category_rate = stats['total_categories_found'] / stats['urls_processed']
            if category_rate < MIN_CATEGORIES_THRESHOLD_PER_DEPTH:
                return True
        
        if stats['urls_processed'] >= 3:
            no_category_rate = stats['urls_without_categories'] / stats['urls_processed']
            if no_category_rate > MAX_NO_CATEGORIES_THRESHOLD_PER_DEPTH:
                return True
        
        return False
    
    def is_url_visited(self, url: str) -> bool:
        """Check if a URL has been visited."""
        return url in self.visited_urls


class SmartExplorationController:
    """Controller for smart exploration with early stopping."""
    
    def __init__(self, url_tracker: URLTracker):
        self.url_tracker = url_tracker
        self.depth_exploration_status: Dict[int, bool] = {}
    
    def should_explore_depth(self, depth: int) -> bool:
        """Determine if exploration should continue at this depth."""
        if depth in self.depth_exploration_status:
            return self.depth_exploration_status[depth]
        
        should_stop = self.url_tracker.should_stop_exploration_at_depth(depth)
        self.depth_exploration_status[depth] = not should_stop
        
        return not should_stop
    
    def record_depth_exploration(self, depth: int, categories_found: int):
        """Record exploration results for a depth level."""
        self.url_tracker.update_depth_stats(depth, categories_found)


class CategoryMapper:
    """
    Maps ecommerce website categories using AI Scraper with recursive discovery.
    
    Workflow:
    1. Extracts main categories from homepage
    2. Recursively explores category pages for subcategories
    3. Builds hierarchical relationships with breadcrumbs
    4. Supports smart early stopping based on exploration stats
    """
    
    def __init__(
        self,
        api_key: str,
        max_depth: int = 2,
        delay_between_requests: float = 1.0,
        max_concurrent_requests: int = 5,
        max_categories: int = 100,
        render_javascript: bool = False
    ):
        """
        Initialize the CategoryMapper.
        
        Args:
            api_key: Oxylabs AI Studio API key
            max_depth: Maximum depth to explore subcategories (default: 2)
            delay_between_requests: Delay between requests in seconds (default: 1.0)
            max_concurrent_requests: Maximum concurrent requests (default: 5)
            max_categories: Maximum categories to extract (default: 100)
            render_javascript: Whether to render JavaScript on pages (default: False)
        """
        self.api_key = api_key
        self.max_depth = max_depth
        self.delay_between_requests = delay_between_requests
        self.max_concurrent_requests = max_concurrent_requests
        self.max_categories = max_categories
        self.render_javascript = render_javascript
        
        self.ai_scraper = AiScraper(api_key=api_key)
        self.logger = logger
        self.rate_limiter = RateLimiter(max_concurrent_requests, delay_between_requests)
        self.url_tracker = URLTracker()
        self.exploration_controller = SmartExplorationController(self.url_tracker)
        self.stop_processing = False
        self.categories_schema = CATEGORY_SCHEMA
        self.discovered_categories = []
        self.domain = None
    
    def _is_valid_domain_url(self, url: str, domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            url_parsed = urlparse(url)
            domain_parsed = urlparse(domain)
            
            url_domain = url_parsed.netloc.lower().lstrip('www.')
            domain_name = domain_parsed.netloc.lower().lstrip('www.')
            
            return url_domain == domain_name
            
        except Exception as e:
            self.logger.warning(f"Error validating domain for URL {url}: {str(e)}")
            return False

    def _create_category_from_data(
        self, 
        cat_data: Dict[str, Any], 
        domain: str, 
        level: int,
    ) -> Optional[Category]:
        """Create a Category object from discovered data."""
        try:
            name = cat_data.get('name', '').strip()
            url = cat_data.get('url', '').strip() if cat_data.get('url') else ''
            # TODO: check if url includes the domain, if not, add it
            if not url.startswith(('http://', 'https://')):
                url = urljoin(domain, url if url.startswith('/') else '/' + url)
                cat_data['url'] = url
            
            parent_category_url = cat_data.get('parent_category_url')
            breadcrumbs = cat_data.get('breadcrumbs', [name])
            
            if not self._is_valid_category_data(cat_data):
                self.logger.warning(f"Skipping category with invalid data: {cat_data}")
                return None
            
            if parent_category_url and parent_category_url not in ['null', 'None', '']:
                if not parent_category_url.startswith(('http://', 'https://')):
                    parent_category_url = urljoin(
                        domain, 
                        parent_category_url if parent_category_url.startswith('/') else '/' + parent_category_url
                    )
                
                if not self._is_valid_domain_url(parent_category_url, domain):
                    self.logger.warning(f"Parent URL is external, setting to None: parent='{parent_category_url}'")
                    parent_category_url = None
            else:
                parent_category_url = None
            
            return Category(
                category_name=name,
                category_breadcrumbs=breadcrumbs,
                category_url=url,
                parent_category_url=parent_category_url,
                level=level,
            )
            
        except Exception as e:
            self.logger.error(f"Error creating category from data: {str(e)}")
            return None
    
    async def _explore_subcategories_async(
        self, 
        category: Category,
    ) -> None:
        """Explore subcategories for a given category asynchronously."""
        try:
            if self.stop_processing:
                self.logger.debug(f"Skipping subcategory exploration for {category.category_name} - processing stopped")
                return
            
            if self.url_tracker.is_url_visited(category.category_url):
                self.logger.debug(f"Skipping already visited URL: {category.category_url}")
                return
            
            self.logger.info(f"Exploring potential subcategories for: {category.category_name}")
            
            await self._explore_categories_recursively(
                category.category_url, category.level + 1
            )
            
        except Exception as e:
            self.logger.error(f"Error exploring subcategories for {category.category_name}: {str(e)}")
            raise
    
    def _is_valid_category_data(self, cat_data: Dict[str, Any]) -> bool:
        """Check if category data is valid."""
        try:
            name = cat_data.get('name')
            url = cat_data.get('url')
            
            if name is None or url is None:
                return False
            
            if not str(name).strip() or not str(url).strip():
                return False
            
            if str(name).lower() in ['none', 'null', ''] or str(url).lower() in ['none', 'null', '']:
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Error validating category data: {str(e)}")
            return False
    
    async def map_categories(self, domain: str) -> CategoryMap:
        """
        Map all categories for an ecommerce domain.
        
        Args:
            domain: The ecommerce domain to map (e.g., "https://example.com")
            
        Returns:
            CategoryMap object containing all discovered categories
        """
        self.logger.info(f"Starting category mapping for domain: {domain}")
        
        if not domain.startswith(('http://', 'https://')):
            domain = f"https://{domain}"
        
        domain = domain.rstrip('/')
        self.domain = domain
        self.discovered_categories = []
        
        self.logger.info("Starting recursive category exploration from homepage")
        await self._explore_categories_recursively(url=domain, level=0)
        
        category_map = CategoryMap(
            domain=domain,
            categories=self.discovered_categories,
            total_categories=len(self.discovered_categories)
        )
        
        self.logger.info(f"Mapping completed. Found {len(self.discovered_categories)} categories")
        self._log_exploration_stats()
        
        return category_map
    
    async def _get_categories_from_page(self, url: str) -> List[Dict[str, Any]]:
        """Get categories from a URL with rate limiting."""
        self.url_tracker.mark_url_visited(url)
        async with self.rate_limiter:
            try:
                if self.stop_processing:
                    self.logger.info("Processing stopped due to category limit")
                    return []
                
                active_requests = self.max_concurrent_requests - self.rate_limiter.semaphore._value
                self.logger.info(f"Making request to {url} (Active: {active_requests}/{self.max_concurrent_requests})")
                
                result = await self.ai_scraper.scrape_async(
                    url=url,
                    output_format="json",
                    schema=self.categories_schema,
                    render_javascript=self.render_javascript
                )
                
                if result.data and isinstance(result.data, dict):
                    categories = result.data.get('categories', [])
                    
                    valid_categories = [
                        cat for cat in categories 
                        if self._is_valid_category_data(cat)
                    ]
                    
                    self.logger.info(
                        f"Extracted {len(valid_categories)} valid categories from {url} "
                        f"(filtered from {len(categories)} total)"
                    )
                    return valid_categories
                
            except Exception as e:
                self.logger.error(f"Failed to get categories from {url}: {str(e)}")
            
            return []
    
    def _log_exploration_stats(self):
        """Log exploration statistics for analysis."""
        self.logger.info("=== Exploration Statistics ===")
        self.logger.info(f"Total URLs visited: {len(self.url_tracker.visited_urls)}")
        self.logger.info(f"Categories found: {len(self.discovered_categories)} / {self.max_categories} (limit)")
        
        for depth in sorted(self.url_tracker.depth_stats.keys()):
            stats = self.url_tracker.depth_stats[depth]
            self.logger.info(f"Depth {depth}: {stats['urls_processed']} URLs, "
                           f"{stats['total_categories_found']} categories found, "
                           f"{stats['urls_with_categories']} URLs with categories")
        
        high_conf_count = sum(1 for _, count in self.url_tracker.categories_found_per_url.items() 
                            if count > 0)
        self.logger.info(f"URLs with categories found: {high_conf_count}/{len(self.url_tracker.visited_urls)}")
    
    async def _explore_categories_recursively(
        self, 
        url: str, 
        level: int
    ) -> None:
        """Recursively explore categories from a URL."""
        
        if self.stop_processing:
            self.logger.info("Processing stopped due to category limit")
            return
        
        if level > self.max_depth:
            self.logger.info(f"Reached maximum depth {self.max_depth}")
            return
        
        if not self.exploration_controller.should_explore_depth(level):
            self.logger.info(f"Smart exploration stopping at depth {level}")
            return
        
        if len(self.discovered_categories) >= self.max_categories:
            self.logger.info(f"Reached maximum categories limit ({self.max_categories})")
            self.stop_processing = True
            return
        
        if self.url_tracker.is_url_visited(url):
            self.logger.debug(f"URL already visited: {url}")
            return
        
        if not self._is_valid_domain_url(url, self.domain):
            self.logger.warning(f"Skipping external URL: {url}")
            return
        
        try:
            self.logger.info(f"Exploring {url} (level {level})")
            
            categories_data = await self._get_categories_from_page(url)
            
            categories_found = len(categories_data) if categories_data else 0
            self.url_tracker.categories_found_per_url[url] = categories_found
            self.exploration_controller.record_depth_exploration(level, categories_found)
            
            if not categories_data:
                return
            
            self.logger.info(f"Found {len(categories_data)} categories at {url}")
            
            categories_to_explore = []
            for cat_data in categories_data:
                if not self._is_valid_category_data(cat_data):
                    self.logger.debug(f"Skipping invalid category data: {cat_data}")
                    continue
                
                category = self._create_category_from_data(
                    cat_data, self.domain, level=level
                )
                
                if not category:
                    continue
                
                if category.category_url not in [c.category_url for c in self.discovered_categories]:
                    if len(self.discovered_categories) < self.max_categories:
                        self.discovered_categories.append(category)
                        categories_to_explore.append(category)
                        self.logger.info(
                            f"Added category: {category.category_name} "
                            f"(level {level}, total: {len(self.discovered_categories)}/{self.max_categories})"
                        )
                    else:
                        self.logger.info(f"Reached maximum categories limit ({self.max_categories})")
                        self.stop_processing = True
                        break
            
            if len(self.discovered_categories) >= self.max_categories:
                self.logger.info(f"Reached maximum categories limit ({self.max_categories})")
                self.stop_processing = True
                return
            
            if not self.stop_processing and categories_to_explore:
                tasks = [
                    self._explore_subcategories_async(category)
                    for category in categories_to_explore
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        self.logger.error(f"Error exploring subcategories: {result}")
            
        except Exception as e:
            self.logger.error(f"Error exploring {url}: {str(e)}")
            self.url_tracker.mark_url_visited(url, 0)
    
    def map_categories_sync(self, domain: str) -> CategoryMap:
        """
        Synchronous wrapper for map_categories.
        
        Args:
            domain: The ecommerce domain to map
            
        Returns:
            CategoryMap with all discovered categories
        """
        return asyncio.run(self.map_categories(domain))
