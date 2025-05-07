import os
import json
import time
import logging
import hashlib
from threading import Lock
from typing import Any, Dict, Optional
from config import CACHE_DIR, CACHE_TTL

# Configure logging
logger = logging.getLogger(__name__)

class MemoryCache:
    """Simple in-memory cache with expiration"""
    
    def __init__(self, max_size=100, ttl=3600):
        """
        Initialize memory cache
        
        Args:
            max_size (int): Maximum number of items to store
            ttl (int): Default time-to-live in seconds
        """
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.default_ttl = ttl
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key (str): Cache key
            
        Returns:
            Any: Cached value or None if not found or expired
        """
        with self.lock:
            if key in self.cache:
                # Check if expired
                if time.time() - self.access_times[key]['created'] > self.access_times[key]['ttl']:
                    # Remove expired item
                    self.cache.pop(key)
                    self.access_times.pop(key)
                    return None
                
                # Update last access time
                self.access_times[key]['accessed'] = time.time()
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (int, optional): Time-to-live in seconds
        """
        if ttl is None:
            ttl = self.default_ttl
            
        with self.lock:
            # If cache is full, remove least recently used item
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._remove_lru()
            
            # Add or update item
            self.cache[key] = value
            self.access_times[key] = {
                'created': time.time(),
                'accessed': time.time(),
                'ttl': ttl
            }
    
    def delete(self, key: str) -> bool:
        """
        Delete item from cache
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: True if item was deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
                self.access_times.pop(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def _remove_lru(self) -> None:
        """Remove least recently used item"""
        if not self.access_times:
            return
            
        # Find least recently accessed item
        lru_key = min(self.access_times.items(), key=lambda x: x[1]['accessed'])[0]
        
        # Remove item
        self.cache.pop(lru_key)
        self.access_times.pop(lru_key)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics
        
        Returns:
            dict: Cache statistics
        """
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': 0,  # Not tracked in this implementation
                'misses': 0  # Not tracked in this implementation
            }

class DiskCache:
    """File-based cache with expiration"""
    
    def __init__(self, cache_dir=CACHE_DIR, ttl=CACHE_TTL):
        """
        Initialize disk cache
        
        Args:
            cache_dir (str): Directory to store cache files
            ttl (int): Default time-to-live in seconds
        """
        self.cache_dir = cache_dir
        self.default_ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create subdirectories
        self.llm_cache_dir = os.path.join(cache_dir, 'llm')
        self.audio_cache_dir = os.path.join(cache_dir, 'audio')
        os.makedirs(self.llm_cache_dir, exist_ok=True)
        os.makedirs(self.audio_cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str, cache_type: str = 'llm') -> str:
        """
        Get path for cache file
        
        Args:
            key (str): Cache key
            cache_type (str): Type of cache ('llm' or 'audio')
            
        Returns:
            str: Path to cache file
        """
        # Create hash of key for safe filename
        hash_key = hashlib.md5(key.encode()).hexdigest()
        
        # Get appropriate cache directory
        if cache_type == 'audio':
            cache_dir = self.audio_cache_dir
        else:
            cache_dir = self.llm_cache_dir
            
        return os.path.join(cache_dir, f"{hash_key}.json")
    
    def get(self, key: str, cache_type: str = 'llm') -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key (str): Cache key
            cache_type (str): Type of cache ('llm' or 'audio')
            
        Returns:
            Any: Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key, cache_type)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Check if expired
                if 'expiry' in cache_data and time.time() > cache_data['expiry']:
                    # Remove expired item
                    os.remove(cache_path)
                    return None
                
                return cache_data['value']
            except Exception as e:
                logger.error(f"Error reading cache file {cache_path}: {e}")
                
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, cache_type: str = 'llm') -> None:
        """
        Set value in cache
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (int, optional): Time-to-live in seconds
            cache_type (str): Type of cache ('llm' or 'audio')
        """
        if ttl is None:
            ttl = self.default_ttl
            
        cache_path = self._get_cache_path(key, cache_type)
        
        try:
            cache_data = {
                'value': value,
                'created': time.time(),
                'expiry': time.time() + ttl
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error writing cache file {cache_path}: {e}")
    
    def delete(self, key: str, cache_type: str = 'llm') -> bool:
        """
        Delete item from cache
        
        Args:
            key (str): Cache key
            cache_type (str): Type of cache ('llm' or 'audio')
            
        Returns:
            bool: True if item was deleted, False if not found
        """
        cache_path = self._get_cache_path(key, cache_type)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except Exception as e:
                logger.error(f"Error deleting cache file {cache_path}: {e}")
                
        return False
    
    def clear(self, cache_type: Optional[str] = None) -> None:
        """
        Clear cache
        
        Args:
            cache_type (str, optional): Type of cache to clear ('llm', 'audio' or None for all)
        """
        if cache_type == 'llm':
            cache_dirs = [self.llm_cache_dir]
        elif cache_type == 'audio':
            cache_dirs = [self.audio_cache_dir]
        else:
            cache_dirs = [self.llm_cache_dir, self.audio_cache_dir]
            
        for cache_dir in cache_dirs:
            for filename in os.listdir(cache_dir):
                if filename.endswith('.json'):
                    try:
                        os.remove(os.path.join(cache_dir, filename))
                    except Exception as e:
                        logger.error(f"Error deleting cache file {filename}: {e}")
    
    def clear_expired(self) -> int:
        """
        Clear expired cache items
        
        Returns:
            int: Number of items cleared
        """
        count = 0
        
        for cache_dir in [self.llm_cache_dir, self.audio_cache_dir]:
            for filename in os.listdir(cache_dir):
                if filename.endswith('.json'):
                    try:
                        cache_path = os.path.join(cache_dir, filename)
                        
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        # Check if expired
                        if 'expiry' in cache_data and time.time() > cache_data['expiry']:
                            os.remove(cache_path)
                            count += 1
                            
                    except Exception as e:
                        logger.error(f"Error checking cache file {filename}: {e}")
        
        return count
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics
        
        Returns:
            dict: Cache statistics
        """
        stats = {
            'llm_count': 0,
            'audio_count': 0,
            'llm_size': 0,  # Size in bytes
            'audio_size': 0,  # Size in bytes
            'expired_count': 0
        }
        
        # Count LLM cache items
        for filename in os.listdir(self.llm_cache_dir):
            if filename.endswith('.json'):
                stats['llm_count'] += 1
                try:
                    stats['llm_size'] += os.path.getsize(os.path.join(self.llm_cache_dir, filename))
                    
                    # Check if expired
                    with open(os.path.join(self.llm_cache_dir, filename), 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if 'expiry' in cache_data and time.time() > cache_data['expiry']:
                        stats['expired_count'] += 1
                        
                except Exception:
                    pass
        
        # Count audio cache items
        for filename in os.listdir(self.audio_cache_dir):
            if filename.endswith('.json'):
                stats['audio_count'] += 1
                try:
                    stats['audio_size'] += os.path.getsize(os.path.join(self.audio_cache_dir, filename))
                    
                    # Check if expired
                    with open(os.path.join(self.audio_cache_dir, filename), 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if 'expiry' in cache_data and time.time() > cache_data['expiry']:
                        stats['expired_count'] += 1
                        
                except Exception:
                    pass
        
        return stats

# Global cache instances
memory_cache = MemoryCache(max_size=100, ttl=3600)  # 1 hour TTL
disk_cache = DiskCache()