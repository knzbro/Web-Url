#!/usr/bin/env python3
# app.py - Website URL Extractor (Terminal Version)
# Yeh tool terminal mein saara output dikhayega

import requests
from urllib.parse import urljoin, urlparse
import re
import time
from collections import deque
import sys

class TerminalURLExtractor:
    def __init__(self, base_url, max_urls=100, delay=1):
        self.base_url = base_url.rstrip('/')
        self.max_urls = max_urls
        self.delay = delay
        self.visited_urls = set()
        self.all_urls = set()
        self.internal_urls = set()
        self.external_urls = set()
        self.broken_urls = set()
        
        # Headers for request
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Get domain
        parsed = urlparse(self.base_url)
        self.domain = parsed.netloc
        
        # URL pattern
        self.url_pattern = re.compile(r'(?:href|src)=["\']([^"\'>]+)["\']')
    
    def get_absolute_url(self, url, current_url):
        """Convert relative URL to absolute"""
        try:
            if url.startswith(('http://', 'https://')):
                return url
            elif url.startswith('//'):
                return 'https:' + url
            elif url.startswith('/'):
                parsed = urlparse(current_url)
                return f"{parsed.scheme}://{parsed.netloc}{url}"
            else:
                return urljoin(current_url, url)
        except:
            return None
    
    def extract_urls(self, url):
        """Extract URLs from a page"""
        try:
            print(f"  📥 Fetching: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"  ⚠️  HTTP {response.status_code}")
                self.broken_urls.add(url)
                return []
            
            # Find all URLs using regex
            urls = []
            for match in self.url_pattern.finditer(response.text):
                found_url = match.group(1)
                
                # Skip unwanted URLs
                if (found_url.startswith(('#', 'javascript:', 'mailto:', 'tel:')) or
                    found_url.endswith(('.css', '.js', '.png', '.jpg', '.gif'))):
                    continue
                
                # Convert to absolute URL
                abs_url = self.get_absolute_url(found_url, url)
                if abs_url:
                    urls.append(abs_url)
            
            return list(set(urls))  # Remove duplicates
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
            self.broken_urls.add(url)
            return []
    
    def is_internal(self, url):
        """Check if URL is internal"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain or parsed.netloc == ''
    
    def run(self):
        """Main function to run the extractor"""
        print("\n" + "="*60)
        print(" WEBSITE URL EXTRACTOR - TERMINAL VERSION")
        print("="*60)
        print(f"📌 Website: {self.base_url}")
        print(f"📊 Max URLs: {self.max_urls}")
        print(f"⏱️  Delay: {self.delay}s")
        print("-"*60)
        
        queue = deque([self.base_url])
        self.visited_urls.add(self.base_url)
        
        try:
            while queue and len(self.all_urls) < self.max_urls:
                current_url = queue.popleft()
                
                print(f"\n🔍 [{len(self.all_urls)}/{self.max_urls}] {current_url}")
                
                # Extract URLs
                found_urls = self.extract_urls(current_url)
                
                # Process URLs
                new_count = 0
                for url in found_urls:
                    if url not in self.all_urls:
                        self.all_urls.add(url)
                        new_count += 1
                        
                        if self.is_internal(url):
                            self.internal_urls.add(url)
                            if url not in self.visited_urls:
                                queue.append(url)
                                self.visited_urls.add(url)
                        else:
                            self.external_urls.add(url)
                
                print(f"  ✅ Found {new_count} new URLs")
                
                # Show recent URLs
                if new_count > 0:
                    print(f"  📋 Recent: {', '.join(list(found_urls)[:3])}")
                
                time.sleep(self.delay)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        
        # Final Summary
        self.print_summary()
    
    def print_summary(self):
        """Print complete summary"""
        print("\n" + "="*60)
        print(" FINAL SUMMARY")
        print("="*60)
        print(f"\n📌 BASE URL: {self.base_url}")
        print(f"🌐 DOMAIN: {self.domain}")
        print("\n📊 STATISTICS:")
        print(f"   ├─ Total URLs: {len(self.all_urls)}")
        print(f"   ├─ Internal URLs: {len(self.internal_urls)}")
        print(f"   ├─ External URLs: {len(self.external_urls)}")
        print(f"   └─ Broken URLs: {len(self.broken_urls)}")
        
        # Internal URLs
        if self.internal_urls:
            print("\n🏠 INTERNAL URLS:")
            for i, url in enumerate(sorted(self.internal_urls)[:15], 1):
                print(f"   {i:2d}. {url}")
            if len(self.internal_urls) > 15:
                print(f"   ... aur {len(self.internal_urls) - 15} aur")
        
        # External URLs
        if self.external_urls:
            print("\n🌍 EXTERNAL URLS:")
            for i, url in enumerate(sorted(self.external_urls)[:10], 1):
                print(f"   {i:2d}. {url}")
            if len(self.external_urls) > 10:
                print(f"   ... aur {len(self.external_urls) - 10} aur")
        
        # Broken URLs
        if self.broken_urls:
            print("\n💔 BROKEN URLS:")
            for i, url in enumerate(sorted(self.broken_urls)[:10], 1):
                print(f"   {i:2d}. {url}")
            if len(self.broken_urls) > 10:
                print(f"   ... aur {len(self.broken_urls) - 10} aur")
        
        print("\n" + "="*60)
        print("✅ COMPLETE!")
        print("="*60)

def show_banner():
    """Show MDF banner"""
    print("\n" + "="*60)
    print("███╗   ███╗██████╗ ███████╗")
    print("████╗ ████║██╔══██╗██╔════╝")
    print("██╔████╔██║██║  ██║█████╗  ")
    print("██║╚██╔╝██║██║  ██║██╔══╝  ")
    print("██║ ╚═╝ ██║██████╔╝██║     ")
    print("╚═╝     ╚═╝╚═════╝ ╚═╝     ")
    print("="*60)
    print("         MDF - URL EXTRACTOR")
    print("="*60)

def main():
    """Main function"""
    show_banner()
    
    # Get URL
    url = input("\n🔗 Website URL: ").strip()
    if not url:
        print("❌ URL required!")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"📝 Added https://: {url}")
    
    # Get max URLs
    try:
        max_input = input("📊 Max URLs to extract (default 100): ").strip()
        max_urls = int(max_input) if max_input else 100
    except:
        max_urls = 100
        print("⚠️  Invalid number, using 100")
    
    # Get delay
    try:
        delay_input = input("⏱️  Delay between requests in seconds (default 1): ").strip()
        delay = float(delay_input) if delay_input else 1
    except:
        delay = 1
        print("⚠️  Invalid number, using 1")
    
    # Create and run extractor
    extractor = TerminalURLExtractor(url, max_urls, delay)
    extractor.run()
    
    # Ask to save
    save = input("\n💾 Save to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"urls_{extractor.domain}.txt"
        with open(filename, 'w') as f:
            f.write(f"URLs from {extractor.base_url}\n")
            f.write(f"Total: {len(extractor.all_urls)}\n")
            f.write("-"*40 + "\n\n")
            for url in sorted(extractor.all_urls):
                f.write(url + "\n")
        print(f"✅ Saved to {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
