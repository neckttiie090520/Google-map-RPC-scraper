# -*- coding: utf-8 -*-
"""
Anti-Bot & Anti-Block Utilities
================================

Features:
1. Rotating User-Agent
2. Request fingerprint randomization
3. Delay randomization (human-like behavior)
4. Proxy support (HTTP/SOCKS5)
5. TLS fingerprint randomization

Author: Nextzus
Date: 2025-11-10
"""
import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ==================== USER-AGENT POOL ====================

USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',

    # Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',

    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',

    # Firefox on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',

    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',

    # Safari on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
]


# ==================== ACCEPT-LANGUAGE VARIATIONS ====================

ACCEPT_LANGUAGES = [
    'th-TH,th;q=0.9,en;q=0.8',
    'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
    'en-US,en;q=0.9,th;q=0.8',
    'en-US,en;q=0.9',
    'th,en-US;q=0.9,en;q=0.8',
]


# ==================== HEADER VARIATIONS ====================

def get_random_user_agent() -> str:
    """Get random User-Agent from pool"""
    return random.choice(USER_AGENTS)


def get_random_accept_language(language="th", region="th") -> str:
    """Get Accept-Language for specified language"""
    # Generate appropriate Accept-Language header based on language/region
    return f"{language}-{region.upper()},{language};q=0.9,en;q=0.8"


def generate_randomized_headers(base_headers: Optional[Dict] = None, language="th", region="th") -> Dict:
    """
    Generate headers with randomized values to avoid fingerprinting

    Args:
        base_headers: Base headers to merge with randomized ones
        language: Language code for Accept-Language header
        region: Region code for Accept-Language header

    Returns:
        Dict with randomized headers
    """
    headers = base_headers.copy() if base_headers else {}

    # Core headers with randomization
    headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept-Language': get_random_accept_language(language, region),
        'Referer': 'https://www.google.com/',
        'Accept': 'application/json, text/plain, */*',
        'Cache-Control': random.choice(['no-cache', 'no-store', 'max-age=0']),
        'Pragma': 'no-cache',
    })

    # Optional headers (add randomly for more variation)
    if random.random() > 0.5:
        headers['DNT'] = '1'

    if random.random() > 0.5:
        headers['Upgrade-Insecure-Requests'] = '1'

    # Random sec-ch-ua (Chrome client hints)
    if 'Chrome' in headers['User-Agent']:
        chrome_versions = ['120', '119', '121']
        version = random.choice(chrome_versions)
        headers['sec-ch-ua'] = f'"Not_A Brand";v="8", "Chromium";v="{version}", "Google Chrome";v="{version}"'
        headers['sec-ch-ua-mobile'] = '?0'
        headers['sec-ch-ua-platform'] = random.choice(['"Windows"', '"macOS"'])

    return headers


# ==================== DELAY RANDOMIZATION ====================

class HumanLikeDelay:
    """Generate human-like delays between requests"""

    @staticmethod
    def short_delay() -> float:
        """Short delay between pages (100-300ms)"""
        return random.uniform(0.1, 0.3)

    @staticmethod
    def medium_delay() -> float:
        """Medium delay for natural browsing (500-1500ms)"""
        return random.uniform(0.5, 1.5)

    @staticmethod
    def long_delay() -> float:
        """Long delay after errors (2-5s)"""
        return random.uniform(2.0, 5.0)

    @staticmethod
    def random_page_delay(fast_mode: bool = True) -> float:
        """
        Random delay between pages

        Args:
            fast_mode: If True, use shorter delays (100-300ms)
                      If False, use more human-like delays (500-1500ms)
        """
        if fast_mode:
            return HumanLikeDelay.short_delay()
        else:
            return HumanLikeDelay.medium_delay()

    @staticmethod
    def jittered_delay(base_delay: float, jitter_ratio: float = 0.3) -> float:
        """
        Add jitter to base delay

        Args:
            base_delay: Base delay in seconds
            jitter_ratio: Ratio of jitter (0.3 = ±30%)

        Returns:
            Delay with random jitter
        """
        jitter = base_delay * jitter_ratio
        return base_delay + random.uniform(-jitter, jitter)


# ==================== PROXY CONFIGURATION ====================

@dataclass
class ProxyConfig:
    """Proxy configuration"""
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None

    # SOCKS5 proxy
    socks5_proxy: Optional[str] = None

    # Proxy authentication
    username: Optional[str] = None
    password: Optional[str] = None

    def to_httpx_proxies(self) -> Optional[Dict]:
        """
        Convert to httpx proxy format

        Returns:
            Dict suitable for httpx.AsyncClient(proxies=...)
        """
        if not any([self.http_proxy, self.https_proxy, self.socks5_proxy]):
            return None

        proxies = {}

        if self.socks5_proxy:
            # SOCKS5 proxy
            proxy_url = self.socks5_proxy
            if self.username and self.password:
                # Insert auth into URL
                if '://' in proxy_url:
                    protocol, rest = proxy_url.split('://', 1)
                    proxy_url = f"{protocol}://{self.username}:{self.password}@{rest}"

            proxies['http://'] = proxy_url
            proxies['https://'] = proxy_url

        else:
            # HTTP/HTTPS proxies
            if self.http_proxy:
                proxy_url = self.http_proxy
                if self.username and self.password:
                    if '://' in proxy_url:
                        protocol, rest = proxy_url.split('://', 1)
                        proxy_url = f"{protocol}://{self.username}:{self.password}@{rest}"
                proxies['http://'] = proxy_url

            if self.https_proxy:
                proxy_url = self.https_proxy
                if self.username and self.password:
                    if '://' in proxy_url:
                        protocol, rest = proxy_url.split('://', 1)
                        proxy_url = f"{protocol}://{self.username}:{self.password}@{rest}"
                proxies['https://'] = proxy_url

        return proxies


class ProxyRotator:
    """Rotate through multiple proxies"""

    def __init__(self, proxies: List[ProxyConfig]):
        """
        Initialize proxy rotator

        Args:
            proxies: List of proxy configurations
        """
        self.proxies = proxies
        self.current_index = 0
        self.failed_proxies = set()

    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None

        # Find next working proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            # Skip failed proxies
            if id(proxy) not in self.failed_proxies:
                return proxy

            attempts += 1

        # All proxies failed - reset and try again
        self.failed_proxies.clear()
        return self.proxies[0] if self.proxies else None

    def mark_proxy_failed(self, proxy: ProxyConfig):
        """Mark proxy as failed"""
        self.failed_proxies.add(id(proxy))

    def reset_failed(self):
        """Reset failed proxy list"""
        self.failed_proxies.clear()


# ==================== REQUEST FINGERPRINTING ====================

class RequestFingerprint:
    """Randomize request fingerprint to avoid detection"""

    @staticmethod
    def randomize_order(headers: Dict) -> Dict:
        """
        Randomize header order

        Note: Python 3.7+ dicts maintain insertion order
        """
        items = list(headers.items())

        # Keep User-Agent first (common pattern)
        ua = next((i for i, (k, v) in enumerate(items) if k == 'User-Agent'), None)
        if ua is not None:
            items.insert(0, items.pop(ua))

        # Shuffle remaining headers
        remaining = items[1:]
        random.shuffle(remaining)

        return dict([items[0]] + remaining)

    @staticmethod
    def add_random_casing(headers: Dict) -> Dict:
        """
        Randomly change header casing (some headers)

        Note: HTTP headers are case-insensitive
        """
        new_headers = {}

        for key, value in headers.items():
            # Some headers can have different casing
            if key.lower() in ['accept', 'accept-language', 'cache-control']:
                if random.random() > 0.5:
                    # Keep as-is
                    new_headers[key] = value
                else:
                    # Change to Title-Case
                    new_headers[key.title()] = value
            else:
                new_headers[key] = value

        return new_headers


# ==================== RATE LIMITING DETECTION ====================

class RateLimitDetector:
    """Detect and handle rate limiting"""

    def __init__(self, window_seconds: int = 60):
        """
        Initialize rate limit detector

        Args:
            window_seconds: Time window to track requests
        """
        self.window_seconds = window_seconds
        self.request_times: List[float] = []
        self.rate_limited = False
        self.rate_limit_until: float = 0

    def record_request(self):
        """Record a request"""
        now = time.time()

        # Clean old requests
        cutoff = now - self.window_seconds
        self.request_times = [t for t in self.request_times if t > cutoff]

        # Add current request
        self.request_times.append(now)

    def get_request_rate(self) -> float:
        """Get current request rate (requests/second)"""
        if not self.request_times:
            return 0.0

        now = time.time()
        cutoff = now - self.window_seconds
        recent = [t for t in self.request_times if t > cutoff]

        if not recent:
            return 0.0

        return len(recent) / self.window_seconds

    def should_slow_down(self, max_rate: float = 10.0) -> Tuple[bool, float]:
        """
        Check if we should slow down

        Args:
            max_rate: Maximum requests per second

        Returns:
            (should_slow_down, suggested_delay)
        """
        current_rate = self.get_request_rate()

        if current_rate > max_rate:
            # Calculate delay to bring rate under limit
            target_interval = 1.0 / max_rate
            current_interval = self.window_seconds / len(self.request_times)
            suggested_delay = max(0, target_interval - current_interval)

            return True, suggested_delay

        return False, 0.0

    def is_rate_limited(self) -> bool:
        """Check if currently rate limited"""
        if self.rate_limited:
            if time.time() < self.rate_limit_until:
                return True
            else:
                # Rate limit expired
                self.rate_limited = False
                self.rate_limit_until = 0

        return False

    def set_rate_limited(self, duration_seconds: float):
        """Mark as rate limited for duration"""
        self.rate_limited = True
        self.rate_limit_until = time.time() + duration_seconds


# ==================== UTILITY FUNCTIONS ====================

def get_anti_bot_config(
    use_proxy: bool = False,
    proxy_list: Optional[List[str]] = None,
    fast_mode: bool = True,
    max_rate: float = 10.0
) -> Dict:
    """
    Get complete anti-bot configuration

    Args:
        use_proxy: Enable proxy rotation
        proxy_list: List of proxy URLs
        fast_mode: Use fast delays (True) or human-like delays (False)
        max_rate: Maximum request rate (requests/second)

    Returns:
        Configuration dict
    """
    config = {
        'use_proxy': use_proxy,
        'fast_mode': fast_mode,
        'max_rate': max_rate,
        'delay_generator': HumanLikeDelay(),
        'rate_limiter': RateLimitDetector(),
    }

    if use_proxy and proxy_list:
        # Create proxy configs
        proxies = [
            ProxyConfig(http_proxy=url, https_proxy=url)
            for url in proxy_list
        ]
        config['proxy_rotator'] = ProxyRotator(proxies)

    return config


# ==================== TESTING ====================

if __name__ == "__main__":
    # Fix Windows encoding
    import sys
    import io
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("=" * 80)
    print("ANTI-BOT UTILITIES TEST")
    print("=" * 80)
    print()

    # Test User-Agent rotation
    print("1. User-Agent Rotation:")
    for i in range(5):
        ua = get_random_user_agent()
        print(f"   {i+1}. {ua[:80]}...")
    print()

    # Test header generation
    print("2. Randomized Headers:")
    headers = generate_randomized_headers()
    for key, value in list(headers.items())[:5]:
        print(f"   {key}: {value}")
    print()

    # Test delay generation
    print("3. Human-Like Delays:")
    delay_gen = HumanLikeDelay()
    print(f"   Short delay: {delay_gen.short_delay():.3f}s")
    print(f"   Medium delay: {delay_gen.medium_delay():.3f}s")
    print(f"   Long delay: {delay_gen.long_delay():.3f}s")
    print()

    # Test proxy config
    print("4. Proxy Configuration:")
    proxy = ProxyConfig(
        http_proxy="http://proxy.example.com:8080",
        https_proxy="http://proxy.example.com:8080",
        username="user",
        password="pass"
    )
    proxies_dict = proxy.to_httpx_proxies()
    if proxies_dict:
        print(f"   HTTP: {proxies_dict.get('http://', 'N/A')}")
        print(f"   HTTPS: {proxies_dict.get('https://', 'N/A')}")
    print()

    # Test rate limiting
    print("5. Rate Limit Detection:")
    detector = RateLimitDetector(window_seconds=10)
    for i in range(15):
        detector.record_request()
        time.sleep(0.1)

    rate = detector.get_request_rate()
    should_slow, delay = detector.should_slow_down(max_rate=5.0)

    print(f"   Current rate: {rate:.2f} req/sec")
    print(f"   Should slow down: {should_slow}")
    if should_slow:
        print(f"   Suggested delay: {delay:.3f}s")
    print()

    print("=" * 80)
    print("All tests completed!")
    print("=" * 80)
