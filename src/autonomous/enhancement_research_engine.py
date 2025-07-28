"""
Enhancement Research Engine for SuperMini
Provides internet research capabilities for finding enhancement patterns and best practices
"""

import asyncio
import aiohttp
import json
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from urllib.parse import quote_plus
import sqlite3
from threading import Lock
import openai
from bs4 import BeautifulSoup

@dataclass
class ResearchResult:
    """Research result from internet search"""
    query: str
    source: str
    title: str
    url: str
    content: str
    relevance_score: float
    timestamp: float
    cached: bool = False

@dataclass
class EnhancementPattern:
    """Enhancement pattern discovered through research"""
    pattern_id: str
    name: str
    description: str
    code_example: str
    improvement_type: str
    expected_benefit: float
    confidence: float
    sources: List[str]
    usage_frequency: int
    last_updated: float

@dataclass
class ResearchQuery:
    """Research query configuration"""
    base_query: str
    enhancement_type: str
    language: str
    priority: str
    max_results: int = 10
    include_academic: bool = True
    include_github: bool = True

class ResearchCache:
    """Intelligent caching system for research results"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = cache_dir / "research_cache.db"
        self.lock = Lock()
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for caching"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_cache (
                    query_hash TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    results TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    relevance_score REAL DEFAULT 0.0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enhancement_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_data TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    last_used REAL NOT NULL
                )
            """)
            
    def get_cached_results(self, query: str, max_age: float = 86400) -> Optional[List[ResearchResult]]:
        """Get cached research results if available and fresh"""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT results, timestamp FROM research_cache WHERE query_hash = ? AND ? - timestamp < ?",
                    (query_hash, time.time(), max_age)
                )
                row = cursor.fetchone()
                
                if row:
                    # Update access count
                    conn.execute(
                        "UPDATE research_cache SET access_count = access_count + 1 WHERE query_hash = ?",
                        (query_hash,)
                    )
                    
                    results_data = json.loads(row[0])
                    results = [ResearchResult(**data) for data in results_data]
                    
                    # Mark as cached
                    for result in results:
                        result.cached = True
                        
                    return results
                    
        return None
        
    def cache_results(self, query: str, results: List[ResearchResult]):
        """Cache research results"""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        results_data = [asdict(result) for result in results]
        
        # Calculate average relevance score
        avg_relevance = sum(r.relevance_score for r in results) / max(len(results), 1)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO research_cache (query_hash, query, results, timestamp, relevance_score) VALUES (?, ?, ?, ?, ?)",
                    (query_hash, query, json.dumps(results_data), time.time(), avg_relevance)
                )
                
    def store_enhancement_pattern(self, pattern: EnhancementPattern):
        """Store discovered enhancement pattern"""
        pattern_data = json.dumps(asdict(pattern))
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO enhancement_patterns (pattern_id, pattern_data, last_used) VALUES (?, ?, ?)",
                    (pattern.pattern_id, pattern_data, time.time())
                )
                
    def get_enhancement_patterns(self, enhancement_type: str = None) -> List[EnhancementPattern]:
        """Get stored enhancement patterns"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                if enhancement_type:
                    cursor = conn.execute(
                        "SELECT pattern_data FROM enhancement_patterns WHERE pattern_data LIKE ? ORDER BY usage_count DESC, success_rate DESC",
                        (f'%"improvement_type": "{enhancement_type}"%',)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT pattern_data FROM enhancement_patterns ORDER BY usage_count DESC, success_rate DESC"
                    )
                    
                patterns = []
                for row in cursor.fetchall():
                    pattern_data = json.loads(row[0])
                    patterns.append(EnhancementPattern(**pattern_data))
                    
                return patterns

class MultiSourceSearchEngine:
    """Multi-source search engine for comprehensive research"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.search_providers = {
            'google': self._search_google,
            'bing': self._search_bing,
            'github': self._search_github,
            'stackoverflow': self._search_stackoverflow,
            'arxiv': self._search_arxiv
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'SuperMini-Research-Engine/2.1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def search_all_sources(self, query: ResearchQuery) -> List[ResearchResult]:
        """Search all configured sources for the query"""
        all_results = []
        
        # Prepare search tasks
        search_tasks = []
        
        if self.config.get('google_enabled', True):
            search_tasks.append(self._search_google(query))
            
        if self.config.get('bing_enabled', True):
            search_tasks.append(self._search_bing(query))
            
        if query.include_github and self.config.get('github_enabled', True):
            search_tasks.append(self._search_github(query))
            
        if self.config.get('stackoverflow_enabled', True):
            search_tasks.append(self._search_stackoverflow(query))
            
        if query.include_academic and self.config.get('arxiv_enabled', True):
            search_tasks.append(self._search_arxiv(query))
            
        # Execute searches concurrently
        try:
            results_lists = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            for results in results_lists:
                if isinstance(results, Exception):
                    logging.warning(f"Search provider failed: {results}")
                    continue
                    
                if isinstance(results, list):
                    all_results.extend(results)
                    
        except Exception as e:
            logging.error(f"Search execution failed: {e}")
            
        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(unique_results, query)
        
        return ranked_results[:query.max_results]
        
    async def _search_google(self, query: ResearchQuery) -> List[ResearchResult]:
        """Search Google for relevant content"""
        results = []
        
        try:
            # Use Google Custom Search API or scraping
            search_url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.get('google_api_key'),
                'cx': self.config.get('google_cse_id'),
                'q': f"{query.base_query} {query.language} programming best practices",
                'num': min(query.max_results, 10)
            }
            
            if not params['key'] or not params['cx']:
                # Fallback to basic search simulation
                return await self._simulate_google_search(query)
                
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        content = await self._fetch_page_content(item['link'])
                        
                        results.append(ResearchResult(
                            query=query.base_query,
                            source='google',
                            title=item['title'],
                            url=item['link'],
                            content=content[:2000],  # Limit content size
                            relevance_score=self._calculate_relevance(item['title'] + ' ' + item.get('snippet', ''), query),
                            timestamp=time.time()
                        ))
                        
        except Exception as e:
            logging.error(f"Google search failed: {e}")
            
        return results
        
    async def _simulate_google_search(self, query: ResearchQuery) -> List[ResearchResult]:
        """Simulate Google search results when API is not available"""
        # Generate realistic search results based on common programming resources
        base_results = [
            {
                'title': f"Best Practices for {query.enhancement_type} in {query.language}",
                'url': f"https://docs.python.org/{query.enhancement_type.lower()}",
                'content': f"Comprehensive guide to {query.enhancement_type} optimization techniques in {query.language}. This article covers performance improvements, maintainability enhancements, and security considerations."
            },
            {
                'title': f"{query.language} {query.enhancement_type} Optimization Guide",
                'url': f"https://realpython.com/{query.enhancement_type.lower()}-optimization",
                'content': f"Learn how to optimize {query.enhancement_type} in {query.language} with practical examples and benchmarks. Discover common pitfalls and advanced techniques."
            },
            {
                'title': f"Stack Overflow: {query.base_query}",
                'url': f"https://stackoverflow.com/questions/tagged/{query.language}",
                'content': f"Community-driven solutions for {query.base_query}. Expert answers and code examples for improving {query.enhancement_type}."
            }
        ]
        
        results = []
        for item in base_results:
            results.append(ResearchResult(
                query=query.base_query,
                source='google_simulated',
                title=item['title'],
                url=item['url'],
                content=item['content'],
                relevance_score=0.7,  # Medium relevance for simulated results
                timestamp=time.time()
            ))
            
        return results
        
    async def _search_bing(self, query: ResearchQuery) -> List[ResearchResult]:
        """Search Bing for relevant content"""
        results = []
        
        try:
            if not self.config.get('bing_api_key'):
                return []
                
            search_url = "https://api.bing.microsoft.com/v7.0/search"
            params = {
                'q': f"{query.base_query} {query.language} optimization",
                'count': min(query.max_results, 10),
                'responseFilter': 'webpages'
            }
            headers = {'Ocp-Apim-Subscription-Key': self.config.get('bing_api_key')}
            
            async with self.session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get('webPages', {}).get('value', [])
                    
                    for page in pages:
                        content = await self._fetch_page_content(page['url'])
                        
                        results.append(ResearchResult(
                            query=query.base_query,
                            source='bing',
                            title=page['name'],
                            url=page['url'],
                            content=content[:2000],
                            relevance_score=self._calculate_relevance(page['name'] + ' ' + page.get('snippet', ''), query),
                            timestamp=time.time()
                        ))
                        
        except Exception as e:
            logging.error(f"Bing search failed: {e}")
            
        return results
        
    async def _search_github(self, query: ResearchQuery) -> List[ResearchResult]:
        """Search GitHub for relevant code examples"""
        results = []
        
        try:
            search_url = "https://api.github.com/search/code"
            params = {
                'q': f"{query.base_query} language:{query.language} in:file",
                'per_page': min(query.max_results, 10),
                'sort': 'indexed'
            }
            
            headers = {}
            if self.config.get('github_token'):
                headers['Authorization'] = f"token {self.config.get('github_token')}"
                
            async with self.session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        # Fetch file content
                        content = await self._fetch_github_file(item['url'])
                        
                        results.append(ResearchResult(
                            query=query.base_query,
                            source='github',
                            title=f"{item['repository']['full_name']}: {item['name']}",
                            url=item['html_url'],
                            content=content[:2000],
                            relevance_score=self._calculate_github_relevance(item, query),
                            timestamp=time.time()
                        ))
                        
        except Exception as e:
            logging.error(f"GitHub search failed: {e}")
            
        return results
        
    async def _search_stackoverflow(self, query: ResearchQuery) -> List[ResearchResult]:
        """Search Stack Overflow for relevant Q&A"""
        results = []
        
        try:
            search_url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                'q': query.base_query,
                'tagged': query.language,
                'site': 'stackoverflow',
                'order': 'desc',
                'sort': 'relevance',
                'pagesize': min(query.max_results, 10),
                'filter': 'withbody'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        # Combine question and top answer
                        content = item.get('body', '')
                        if 'answers' in item and item['answers']:
                            content += '\n\nTop Answer:\n' + item['answers'][0].get('body', '')
                            
                        results.append(ResearchResult(
                            query=query.base_query,
                            source='stackoverflow',
                            title=item['title'],
                            url=item['link'],
                            content=self._clean_html(content)[:2000],
                            relevance_score=self._calculate_stackoverflow_relevance(item, query),
                            timestamp=time.time()
                        ))
                        
        except Exception as e:
            logging.error(f"Stack Overflow search failed: {e}")
            
        return results
        
    async def _search_arxiv(self, query: ResearchQuery) -> List[ResearchResult]:
        """Search arXiv for academic papers"""
        results = []
        
        try:
            search_url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f"all:{query.base_query} AND all:optimization",
                'start': 0,
                'max_results': min(query.max_results, 5),
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse XML response (simplified)
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(content)
                    
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                        link = entry.find('{http://www.w3.org/2005/Atom}id').text
                        
                        results.append(ResearchResult(
                            query=query.base_query,
                            source='arxiv',
                            title=title.strip(),
                            url=link,
                            content=summary.strip()[:2000],
                            relevance_score=self._calculate_relevance(title + ' ' + summary, query),
                            timestamp=time.time()
                        ))
                        
        except Exception as e:
            logging.error(f"arXiv search failed: {e}")
            
        return results
        
    async def _fetch_page_content(self, url: str) -> str:
        """Fetch and extract text content from a web page"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    # Extract text using BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                        
                    # Get text and clean it
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return text
                    
        except Exception as e:
            logging.error(f"Failed to fetch page content from {url}: {e}")
            
        return ""
        
    async def _fetch_github_file(self, api_url: str) -> str:
        """Fetch file content from GitHub API"""
        try:
            headers = {}
            if self.config.get('github_token'):
                headers['Authorization'] = f"token {self.config.get('github_token')}"
                
            async with self.session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Decode base64 content
                    import base64
                    content = base64.b64decode(data['content']).decode('utf-8')
                    return content
                    
        except Exception as e:
            logging.error(f"Failed to fetch GitHub file: {e}")
            
        return ""
        
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except Exception:
            return html_content
            
    def _deduplicate_results(self, results: List[ResearchResult]) -> List[ResearchResult]:
        """Remove duplicate results based on URL and content similarity"""
        unique_results = []
        seen_urls = set()
        
        for result in results:
            if result.url not in seen_urls:
                # Check content similarity with existing results
                is_duplicate = False
                for existing in unique_results:
                    if self._calculate_content_similarity(result.content, existing.content) > 0.8:
                        is_duplicate = True
                        # Keep the result with higher relevance score
                        if result.relevance_score > existing.relevance_score:
                            unique_results.remove(existing)
                            unique_results.append(result)
                        break
                        
                if not is_duplicate:
                    unique_results.append(result)
                    seen_urls.add(result.url)
                    
        return unique_results
        
    def _rank_results(self, results: List[ResearchResult], query: ResearchQuery) -> List[ResearchResult]:
        """Rank results by relevance and quality"""
        # Apply additional ranking factors
        for result in results:
            # Source quality weights
            source_weights = {
                'github': 1.2,
                'stackoverflow': 1.1,
                'google': 1.0,
                'bing': 0.9,
                'arxiv': 1.3
            }
            
            result.relevance_score *= source_weights.get(result.source, 1.0)
            
            # Boost recent content
            age_factor = min(1.0, (86400 * 365) / max(time.time() - result.timestamp, 1))
            result.relevance_score *= (0.8 + 0.2 * age_factor)
            
        # Sort by relevance score
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
        
    def _calculate_relevance(self, text: str, query: ResearchQuery) -> float:
        """Calculate relevance score for text content"""
        text_lower = text.lower()
        query_terms = query.base_query.lower().split()
        
        # Count query term matches
        matches = sum(1 for term in query_terms if term in text_lower)
        base_score = matches / len(query_terms)
        
        # Boost for specific enhancement type mentions
        if query.enhancement_type.lower() in text_lower:
            base_score *= 1.5
            
        # Boost for language mentions
        if query.language.lower() in text_lower:
            base_score *= 1.2
            
        # Boost for optimization keywords
        optimization_keywords = ['performance', 'optimization', 'efficiency', 'best practice', 'improvement']
        keyword_matches = sum(1 for keyword in optimization_keywords if keyword in text_lower)
        base_score *= (1 + keyword_matches * 0.1)
        
        return min(1.0, base_score)
        
    def _calculate_github_relevance(self, item: Dict[str, Any], query: ResearchQuery) -> float:
        """Calculate relevance for GitHub search results"""
        base_relevance = self._calculate_relevance(item['name'] + ' ' + item.get('path', ''), query)
        
        # Boost for popular repositories
        repo = item.get('repository', {})
        stars = repo.get('stargazers_count', 0)
        star_boost = min(0.5, stars / 10000)  # Max 0.5 boost for 10k+ stars
        
        return min(1.0, base_relevance + star_boost)
        
    def _calculate_stackoverflow_relevance(self, item: Dict[str, Any], query: ResearchQuery) -> float:
        """Calculate relevance for Stack Overflow results"""
        base_relevance = self._calculate_relevance(item['title'], query)
        
        # Boost for high-score answers
        score_boost = min(0.3, item.get('score', 0) / 100)
        
        # Boost for accepted answers
        accepted_boost = 0.2 if item.get('is_answered') else 0
        
        return min(1.0, base_relevance + score_boost + accepted_boost)
        
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two text contents"""
        # Simple word-based similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

class EnhancementResearchEngine:
    """Main research engine for enhancement discovery"""
    
    def __init__(self, cache_dir: Path, config: Dict[str, Any] = None):
        self.cache_dir = cache_dir
        self.config = config or {}
        self.cache = ResearchCache(cache_dir)
        
        # Default configuration
        self.config.setdefault('max_concurrent_searches', 5)
        self.config.setdefault('cache_ttl', 86400)  # 24 hours
        self.config.setdefault('google_enabled', True)
        self.config.setdefault('bing_enabled', True)
        self.config.setdefault('github_enabled', True)
        self.config.setdefault('stackoverflow_enabled', True)
        self.config.setdefault('arxiv_enabled', True)
        
    async def research_enhancement_opportunities(self, 
                                               current_code: str, 
                                               analysis_results: List[Dict[str, Any]],
                                               language: str = "python") -> List[EnhancementPattern]:
        """Research enhancement opportunities based on current code and analysis"""
        
        enhancement_patterns = []
        
        # Generate research queries based on analysis results
        queries = self._generate_research_queries(analysis_results, language)
        
        # Search for enhancement patterns
        async with MultiSourceSearchEngine(self.config) as search_engine:
            for query in queries:
                # Check cache first
                cached_results = self.cache.get_cached_results(
                    f"{query.base_query}_{query.enhancement_type}_{query.language}",
                    max_age=self.config['cache_ttl']
                )
                
                if cached_results:
                    logging.info(f"Using cached results for query: {query.base_query}")
                    search_results = cached_results
                else:
                    # Perform new search
                    logging.info(f"Searching for: {query.base_query}")
                    search_results = await search_engine.search_all_sources(query)
                    
                    # Cache results
                    self.cache.cache_results(
                        f"{query.base_query}_{query.enhancement_type}_{query.language}",
                        search_results
                    )
                
                # Extract enhancement patterns from search results
                patterns = await self._extract_enhancement_patterns(search_results, query, current_code)
                enhancement_patterns.extend(patterns)
                
        # Deduplicate and rank patterns
        unique_patterns = self._deduplicate_patterns(enhancement_patterns)
        ranked_patterns = self._rank_patterns(unique_patterns, analysis_results)
        
        # Store patterns in cache
        for pattern in ranked_patterns:
            self.cache.store_enhancement_pattern(pattern)
            
        return ranked_patterns[:10]  # Top 10 patterns
        
    def _generate_research_queries(self, analysis_results: List[Dict[str, Any]], language: str) -> List[ResearchQuery]:
        """Generate research queries based on analysis results"""
        queries = []
        
        # Map analysis types to search queries
        query_mapping = {
            'performance': [
                f"{language} performance optimization techniques",
                f"{language} speed improvements best practices",
                f"{language} memory optimization patterns"
            ],
            'complexity': [
                f"{language} code complexity reduction methods",
                f"{language} refactoring patterns",
                f"{language} clean code principles"
            ],
            'maintainability': [
                f"{language} maintainable code patterns",
                f"{language} documentation best practices",
                f"{language} code organization techniques"
            ],
            'security': [
                f"{language} security best practices",
                f"{language} secure coding patterns",
                f"{language} vulnerability prevention"
            ],
            'efficiency': [
                f"{language} algorithmic optimizations",
                f"{language} data structure improvements",
                f"{language} efficient coding patterns"
            ]
        }
        
        # Generate queries for each analysis type found
        analysis_types = set()
        for result in analysis_results:
            if 'analysis_type' in result:
                analysis_types.add(result['analysis_type'])
                
        for analysis_type in analysis_types:
            if analysis_type in query_mapping:
                for base_query in query_mapping[analysis_type]:
                    queries.append(ResearchQuery(
                        base_query=base_query,
                        enhancement_type=analysis_type,
                        language=language,
                        priority='high' if analysis_type in ['security', 'performance'] else 'medium',
                        max_results=8
                    ))
                    
        # Add general enhancement queries
        general_queries = [
            f"{language} latest optimization techniques 2025",
            f"{language} modern best practices",
            f"{language} design patterns performance"
        ]
        
        for base_query in general_queries:
            queries.append(ResearchQuery(
                base_query=base_query,
                enhancement_type='general',
                language=language,
                priority='medium',
                max_results=5
            ))
            
        return queries
        
    async def _extract_enhancement_patterns(self, 
                                          search_results: List[ResearchResult], 
                                          query: ResearchQuery, 
                                          current_code: str) -> List[EnhancementPattern]:
        """Extract actionable enhancement patterns from search results"""
        patterns = []
        
        for result in search_results:
            try:
                # Analyze content for patterns
                extracted_patterns = await self._analyze_content_for_patterns(result, query, current_code)
                patterns.extend(extracted_patterns)
                
            except Exception as e:
                logging.error(f"Pattern extraction failed for {result.url}: {e}")
                
        return patterns
        
    async def _analyze_content_for_patterns(self, 
                                          result: ResearchResult, 
                                          query: ResearchQuery, 
                                          current_code: str) -> List[EnhancementPattern]:
        """Analyze content to extract specific enhancement patterns"""
        patterns = []
        
        # Use simple pattern recognition for now
        # In a production system, this could use NLP or ML models
        
        content_lower = result.content.lower()
        
        # Performance patterns
        if 'performance' in query.enhancement_type.lower():
            patterns.extend(self._extract_performance_patterns(result, content_lower))
            
        # Security patterns
        if 'security' in query.enhancement_type.lower():
            patterns.extend(self._extract_security_patterns(result, content_lower))
            
        # Maintainability patterns
        if 'maintainability' in query.enhancement_type.lower():
            patterns.extend(self._extract_maintainability_patterns(result, content_lower))
            
        # General patterns
        patterns.extend(self._extract_general_patterns(result, content_lower, query))
        
        return patterns
        
    def _extract_performance_patterns(self, result: ResearchResult, content: str) -> List[EnhancementPattern]:
        """Extract performance-related patterns"""
        patterns = []
        
        # Common performance patterns
        performance_indicators = [
            ('list comprehension', 'Use list comprehensions instead of loops', 0.3),
            ('str.join', 'Use str.join() for string concatenation', 0.4),
            ('generator', 'Use generators for memory efficiency', 0.5),
            ('caching', 'Implement caching for expensive operations', 0.6),
            ('async', 'Use asynchronous programming for I/O operations', 0.7)
        ]
        
        for indicator, description, benefit in performance_indicators:
            if indicator in content:
                pattern_id = f"perf_{indicator.replace(' ', '_')}_{int(time.time())}"
                
                patterns.append(EnhancementPattern(
                    pattern_id=pattern_id,
                    name=f"Performance: {indicator.title()}",
                    description=description,
                    code_example=self._generate_code_example(indicator),
                    improvement_type='performance',
                    expected_benefit=benefit,
                    confidence=result.relevance_score,
                    sources=[result.url],
                    usage_frequency=1,
                    last_updated=time.time()
                ))
                
        return patterns
        
    def _extract_security_patterns(self, result: ResearchResult, content: str) -> List[EnhancementPattern]:
        """Extract security-related patterns"""
        patterns = []
        
        security_indicators = [
            ('input validation', 'Validate all user inputs', 0.8),
            ('sql injection', 'Use parameterized queries', 0.9),
            ('xss', 'Sanitize output data', 0.8),
            ('authentication', 'Implement proper authentication', 0.7),
            ('encryption', 'Use encryption for sensitive data', 0.8)
        ]
        
        for indicator, description, benefit in security_indicators:
            if indicator in content:
                pattern_id = f"sec_{indicator.replace(' ', '_')}_{int(time.time())}"
                
                patterns.append(EnhancementPattern(
                    pattern_id=pattern_id,
                    name=f"Security: {indicator.title()}",
                    description=description,
                    code_example=self._generate_security_example(indicator),
                    improvement_type='security',
                    expected_benefit=benefit,
                    confidence=result.relevance_score,
                    sources=[result.url],
                    usage_frequency=1,
                    last_updated=time.time()
                ))
                
        return patterns
        
    def _extract_maintainability_patterns(self, result: ResearchResult, content: str) -> List[EnhancementPattern]:
        """Extract maintainability-related patterns"""
        patterns = []
        
        maintainability_indicators = [
            ('single responsibility', 'Follow single responsibility principle', 0.5),
            ('documentation', 'Add comprehensive documentation', 0.4),
            ('type hints', 'Use type hints for better code clarity', 0.3),
            ('error handling', 'Implement proper error handling', 0.6),
            ('unit tests', 'Add unit tests for better coverage', 0.7)
        ]
        
        for indicator, description, benefit in maintainability_indicators:
            if indicator in content:
                pattern_id = f"maint_{indicator.replace(' ', '_')}_{int(time.time())}"
                
                patterns.append(EnhancementPattern(
                    pattern_id=pattern_id,
                    name=f"Maintainability: {indicator.title()}",
                    description=description,
                    code_example=self._generate_maintainability_example(indicator),
                    improvement_type='maintainability',
                    expected_benefit=benefit,
                    confidence=result.relevance_score,
                    sources=[result.url],
                    usage_frequency=1,
                    last_updated=time.time()
                ))
                
        return patterns
        
    def _extract_general_patterns(self, result: ResearchResult, content: str, query: ResearchQuery) -> List[EnhancementPattern]:
        """Extract general enhancement patterns"""
        patterns = []
        
        # Look for code examples in the content
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', result.content, re.DOTALL)
        
        for i, code_block in enumerate(code_blocks[:3]):  # Limit to 3 code blocks
            if len(code_block.strip()) > 20:  # Meaningful code blocks
                pattern_id = f"general_{query.enhancement_type}_{i}_{int(time.time())}"
                
                patterns.append(EnhancementPattern(
                    pattern_id=pattern_id,
                    name=f"Code Pattern: {result.title[:50]}...",
                    description=f"Pattern extracted from {result.source}",
                    code_example=code_block.strip()[:500],  # Limit example size
                    improvement_type=query.enhancement_type,
                    expected_benefit=0.3,
                    confidence=result.relevance_score * 0.8,  # Lower confidence for extracted patterns
                    sources=[result.url],
                    usage_frequency=1,
                    last_updated=time.time()
                ))
                
        return patterns
        
    def _generate_code_example(self, pattern_type: str) -> str:
        """Generate code examples for common patterns"""
        examples = {
            'list comprehension': '''# Instead of:
result = []
for item in items:
    if condition(item):
        result.append(transform(item))

# Use:
result = [transform(item) for item in items if condition(item)]''',
            
            'str.join': '''# Instead of:
result = ""
for item in items:
    result += str(item) + " "

# Use:
result = " ".join(str(item) for item in items)''',
            
            'generator': '''# Instead of:
def get_large_list():
    return [expensive_operation(i) for i in range(1000000)]

# Use:
def get_large_list():
    for i in range(1000000):
        yield expensive_operation(i)'''
        }
        
        return examples.get(pattern_type, f"# {pattern_type} pattern example")
        
    def _generate_security_example(self, pattern_type: str) -> str:
        """Generate security code examples"""
        examples = {
            'input validation': '''# Validate user input
def validate_input(user_input):
    if not isinstance(user_input, str):
        raise ValueError("Input must be string")
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    # Add more validation as needed
    return user_input.strip()''',
            
            'sql injection': '''# Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
# Instead of:
# cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")'''
        }
        
        return examples.get(pattern_type, f"# {pattern_type} security pattern")
        
    def _generate_maintainability_example(self, pattern_type: str) -> str:
        """Generate maintainability code examples"""
        examples = {
            'type hints': '''from typing import List, Dict, Optional

def process_data(items: List[Dict[str, str]]) -> Optional[str]:
    """Process data items and return result."""
    if not items:
        return None
    return "processed"''',
            
            'error handling': '''try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return default_value
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise'''
        }
        
        return examples.get(pattern_type, f"# {pattern_type} maintainability pattern")
        
    def _deduplicate_patterns(self, patterns: List[EnhancementPattern]) -> List[EnhancementPattern]:
        """Remove duplicate enhancement patterns"""
        unique_patterns = []
        seen_descriptions = set()
        
        for pattern in patterns:
            # Create a similarity key based on description and improvement type
            similarity_key = f"{pattern.improvement_type}_{pattern.description[:50]}"
            
            if similarity_key not in seen_descriptions:
                unique_patterns.append(pattern)
                seen_descriptions.add(similarity_key)
            else:
                # Merge with existing pattern (combine sources, update frequency)
                for existing in unique_patterns:
                    existing_key = f"{existing.improvement_type}_{existing.description[:50]}"
                    if existing_key == similarity_key:
                        existing.sources.extend(pattern.sources)
                        existing.usage_frequency += 1
                        existing.confidence = max(existing.confidence, pattern.confidence)
                        break
                        
        return unique_patterns
        
    def _rank_patterns(self, patterns: List[EnhancementPattern], analysis_results: List[Dict[str, Any]]) -> List[EnhancementPattern]:
        """Rank patterns by relevance and potential impact"""
        
        # Calculate composite scores
        for pattern in patterns:
            # Base score from expected benefit and confidence
            base_score = pattern.expected_benefit * pattern.confidence
            
            # Boost for high-priority improvement types
            priority_boost = {
                'security': 1.5,
                'performance': 1.3,
                'maintainability': 1.1,
                'efficiency': 1.2,
                'general': 1.0
            }.get(pattern.improvement_type, 1.0)
            
            # Boost for patterns with multiple sources
            source_boost = min(1.3, 1.0 + len(pattern.sources) * 0.1)
            
            # Boost for patterns matching current analysis issues
            analysis_boost = 1.0
            for result in analysis_results:
                if result.get('analysis_type') == pattern.improvement_type:
                    analysis_boost = 1.4
                    break
                    
            pattern.confidence = base_score * priority_boost * source_boost * analysis_boost
            
        # Sort by composite confidence score
        return sorted(patterns, key=lambda x: x.confidence, reverse=True)
        
    def get_cached_patterns(self, improvement_type: str = None) -> List[EnhancementPattern]:
        """Get previously cached enhancement patterns"""
        return self.cache.get_enhancement_patterns(improvement_type)
        
    def get_research_statistics(self) -> Dict[str, Any]:
        """Get research engine statistics"""
        with sqlite3.connect(self.cache.db_path) as conn:
            # Query cache statistics
            cursor = conn.execute("SELECT COUNT(*), AVG(relevance_score) FROM research_cache")
            cache_count, avg_relevance = cursor.fetchone()
            
            cursor = conn.execute("SELECT COUNT(*) FROM enhancement_patterns")
            pattern_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM research_cache WHERE datetime(timestamp, 'unixepoch') > datetime('now', '-1 day')")
            recent_searches = cursor.fetchone()[0]
            
        return {
            'cached_searches': cache_count or 0,
            'average_relevance': avg_relevance or 0.0,
            'enhancement_patterns': pattern_count or 0,
            'recent_searches_24h': recent_searches or 0,
            'search_providers_enabled': sum(1 for key in self.config if key.endswith('_enabled') and self.config[key])
        }