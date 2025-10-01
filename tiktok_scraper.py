#!/usr/bin/env python3
"""
TikTok Profile Scraper - Deep Scraping Version
Scrapes account and activity information from TikTok profiles
"""

import json
import time
import re
from playwright.sync_api import sync_playwright
from datetime import datetime


class TikTokScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.page = None
    
    def start(self):
        """Initialize the browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        # Set a realistic user agent
        self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def close(self):
        """Close the browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def scrape_profile(self, username, deep_scrape=True):
        """
        Scrape profile information from a TikTok username
        
        Args:
            username: TikTok username (with or without @)
            deep_scrape: If True, extract embedded JSON data
        
        Returns:
            dict: Profile data including account info and posts
        """
        # Clean username
        username = username.strip()
        if username.startswith('@'):
            username = username[1:]
        
        url = f"https://www.tiktok.com/@{username}"
        print(f"Scraping profile: {url}")
        
        try:
            # Navigate to profile
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(5)  # Wait for dynamic content to load
            
            # Take screenshot for debugging
            self.page.screenshot(path=f"{username}_screenshot.png")
            print(f"Screenshot saved: {username}_screenshot.png")
            
            profile_data = {
                'username': username,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'account_info': {},
                'videos': [],
                'raw_json_data': None,
                'page_metadata': {}
            }
            
            # Extract account information
            profile_data['account_info'] = self._extract_account_info()
            
            # Extract embedded JSON data (deep scrape)
            if deep_scrape:
                print("Performing deep scrape...")
                profile_data['raw_json_data'] = self._extract_embedded_json()
                profile_data['page_metadata'] = self._extract_page_metadata()
            
            # Scroll and extract video information
            profile_data['videos'] = self._extract_videos(scroll=True)
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'username': username,
                'url': url
            }
    
    def _extract_account_info(self):
        """Extract account information from the profile page"""
        info = {}
        
        try:
            # Try to extract display name
            try:
                display_name = self.page.locator('h1[data-e2e="user-title"]').first.inner_text(timeout=5000)
                info['display_name'] = display_name
            except:
                info['display_name'] = None
            
            # Try to extract bio/description
            try:
                bio = self.page.locator('h2[data-e2e="user-bio"]').first.inner_text(timeout=5000)
                info['bio'] = bio
            except:
                info['bio'] = None
            
            # Try to extract follower count
            try:
                follower_element = self.page.locator('[data-e2e="followers-count"]').first
                follower_count = follower_element.inner_text(timeout=5000)
                info['followers'] = follower_count
            except:
                info['followers'] = None
            
            # Try to extract following count
            try:
                following_element = self.page.locator('[data-e2e="following-count"]').first
                following_count = following_element.inner_text(timeout=5000)
                info['following'] = following_count
            except:
                info['following'] = None
            
            # Try to extract likes count
            try:
                likes_element = self.page.locator('[data-e2e="likes-count"]').first
                likes_count = likes_element.inner_text(timeout=5000)
                info['likes'] = likes_count
            except:
                info['likes'] = None
            
            # Try to extract verified status
            try:
                verified = self.page.locator('svg[data-e2e="verified-badge"]').count() > 0
                info['verified'] = verified
            except:
                info['verified'] = False
            
            # Try to extract profile picture URL
            try:
                avatar = self.page.locator('img[data-e2e="user-avatar"]').first.get_attribute('src', timeout=5000)
                info['avatar_url'] = avatar
            except:
                info['avatar_url'] = None
            
            # Try to get additional info from page content
            try:
                page_content = self.page.content()
                # Look for JSON-LD data
                if '__UNIVERSAL_DATA_FOR_REHYDRATION__' in page_content:
                    info['has_structured_data'] = True
                else:
                    info['has_structured_data'] = False
            except:
                pass
            
        except Exception as e:
            print(f"Error extracting account info: {e}")
        
        return info
    
    def _extract_embedded_json(self):
        """Extract embedded JSON data from the page"""
        try:
            page_content = self.page.content()
            
            # Try to find SIGI_STATE (TikTok's embedded data)
            sigi_pattern = r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
            sigi_match = re.search(sigi_pattern, page_content, re.DOTALL)
            
            if sigi_match:
                print("Found SIGI_STATE data")
                try:
                    sigi_data = json.loads(sigi_match.group(1))
                    return {
                        'type': 'SIGI_STATE',
                        'data': sigi_data
                    }
                except json.JSONDecodeError as e:
                    print(f"Error parsing SIGI_STATE: {e}")
            
            # Try to find __UNIVERSAL_DATA_FOR_REHYDRATION__
            universal_pattern = r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>'
            universal_match = re.search(universal_pattern, page_content, re.DOTALL)
            
            if universal_match:
                print("Found __UNIVERSAL_DATA_FOR_REHYDRATION__ data")
                try:
                    universal_data = json.loads(universal_match.group(1))
                    return {
                        'type': '__UNIVERSAL_DATA_FOR_REHYDRATION__',
                        'data': universal_data
                    }
                except json.JSONDecodeError as e:
                    print(f"Error parsing __UNIVERSAL_DATA_FOR_REHYDRATION__: {e}")
            
            # Try alternate patterns
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, page_content, re.DOTALL)
            
            if json_ld_matches:
                print(f"Found {len(json_ld_matches)} JSON-LD blocks")
                json_ld_data = []
                for match in json_ld_matches:
                    try:
                        json_ld_data.append(json.loads(match))
                    except:
                        pass
                
                if json_ld_data:
                    return {
                        'type': 'JSON-LD',
                        'data': json_ld_data
                    }
            
            print("No embedded JSON data found")
            return None
            
        except Exception as e:
            print(f"Error extracting embedded JSON: {e}")
            return None
    
    def _extract_page_metadata(self):
        """Extract page metadata and additional information"""
        metadata = {}
        
        try:
            # Extract meta tags
            meta_tags = self.page.locator('meta').all()
            metadata['meta_tags'] = {}
            
            for meta in meta_tags[:50]:  # Limit to first 50
                try:
                    name = meta.get_attribute('name') or meta.get_attribute('property')
                    content = meta.get_attribute('content')
                    if name and content:
                        metadata['meta_tags'][name] = content
                except:
                    pass
            
            # Get page title
            try:
                metadata['page_title'] = self.page.title()
            except:
                metadata['page_title'] = None
            
            # Get canonical URL
            try:
                canonical = self.page.locator('link[rel="canonical"]').first.get_attribute('href')
                metadata['canonical_url'] = canonical
            except:
                metadata['canonical_url'] = None
            
            # Get Open Graph data
            og_data = {}
            for tag in ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']:
                try:
                    content = self.page.locator(f'meta[property="{tag}"]').first.get_attribute('content')
                    og_data[tag] = content
                except:
                    og_data[tag] = None
            
            metadata['open_graph'] = og_data
            
            # Get Twitter Card data
            twitter_data = {}
            for tag in ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']:
                try:
                    content = self.page.locator(f'meta[name="{tag}"]').first.get_attribute('content')
                    twitter_data[tag] = content
                except:
                    twitter_data[tag] = None
            
            metadata['twitter_card'] = twitter_data
            
        except Exception as e:
            print(f"Error extracting page metadata: {e}")
        
        return metadata
    
    def _extract_videos(self, scroll=False):
        """Extract video information from the profile"""
        videos = []
        
        try:
            # Scroll down to load more videos if requested
            if scroll:
                print("Scrolling to load more videos...")
                for i in range(3):  # Scroll 3 times
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                print("Finished scrolling")
            
            # Try multiple selectors for video elements
            selectors = [
                '[data-e2e="user-post-item"]',
                'div[class*="DivItemContainer"]',
                'div[class*="video"]',
                'a[href*="/video/"]'
            ]
            
            video_elements = []
            for selector in selectors:
                try:
                    elements = self.page.locator(selector).all()
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        video_elements = elements
                        break
                except:
                    continue
            
            if not video_elements:
                print("No video elements found with any selector")
                # Try to find any links to videos in the page
                try:
                    all_links = self.page.locator('a').all()
                    video_links = []
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and '/video/' in href:
                            video_links.append(href)
                    
                    print(f"Found {len(video_links)} video links in page")
                    for link in video_links[:20]:
                        videos.append({
                            'url': f"https://www.tiktok.com{link}" if link.startswith('/') else link,
                            'thumbnail': None,
                            'description': None,
                            'views': None
                        })
                except Exception as e:
                    print(f"Error finding video links: {e}")
                
                return videos
            
            print(f"Processing {len(video_elements)} video elements")
            
            for i, video_element in enumerate(video_elements[:30]):  # Limit to first 30 videos
                try:
                    video_data = {
                        'index': i
                    }
                    
                    # Try to get video link
                    try:
                        video_link = video_element.locator('a').first.get_attribute('href', timeout=2000)
                        if not video_link:
                            video_link = video_element.get_attribute('href', timeout=2000)
                        
                        if video_link:
                            video_data['url'] = f"https://www.tiktok.com{video_link}" if video_link.startswith('/') else video_link
                        else:
                            video_data['url'] = None
                    except:
                        video_data['url'] = None
                    
                    # Try to get thumbnail
                    try:
                        thumbnail = video_element.locator('img').first.get_attribute('src', timeout=2000)
                        video_data['thumbnail'] = thumbnail
                    except:
                        video_data['thumbnail'] = None
                    
                    # Try to get video description (alt text)
                    try:
                        description = video_element.locator('img').first.get_attribute('alt', timeout=2000)
                        video_data['description'] = description
                    except:
                        video_data['description'] = None
                    
                    # Try to get view count
                    try:
                        views = video_element.locator('[data-e2e="video-views"]').first.inner_text(timeout=2000)
                        video_data['views'] = views
                    except:
                        try:
                            # Try alternate selector for views
                            views = video_element.locator('strong').first.inner_text(timeout=2000)
                            video_data['views'] = views
                        except:
                            video_data['views'] = None
                    
                    # Only add if we got at least a URL
                    if video_data['url']:
                        videos.append(video_data)
                    
                except Exception as e:
                    print(f"Error extracting video {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error extracting videos: {e}")
            import traceback
            traceback.print_exc()
        
        return videos
    
    def save_to_file(self, data, filename='tiktok_profile_data.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
        
        # Calculate file size
        import os
        file_size = os.path.getsize(filename)
        if file_size > 1024 * 1024:
            print(f"File size: {file_size / (1024 * 1024):.2f} MB")
        elif file_size > 1024:
            print(f"File size: {file_size / 1024:.2f} KB")
        else:
            print(f"File size: {file_size} bytes")
    
    def print_summary(self, data):
        """Print a summary of scraped data"""
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        
        print(f"\n👤 Profile: @{data['username']}")
        print(f"🔗 URL: {data['url']}")
        print(f"⏰ Scraped: {data['scraped_at']}")
        
        if data.get('account_info'):
            info = data['account_info']
            print(f"\n📊 Account Stats:")
            print(f"  • Display Name: {info.get('display_name', 'N/A')}")
            print(f"  • Bio: {info.get('bio', 'N/A')}")
            print(f"  • Followers: {info.get('followers', 'N/A')}")
            print(f"  • Following: {info.get('following', 'N/A')}")
            print(f"  • Total Likes: {info.get('likes', 'N/A')}")
            print(f"  • Verified: {'✓' if info.get('verified') else '✗'}")
        
        if data.get('videos'):
            print(f"\n🎬 Videos Found: {len(data['videos'])}")
            for i, video in enumerate(data['videos'][:5]):
                print(f"  {i+1}. {video.get('url', 'N/A')}")
                if video.get('views'):
                    print(f"     Views: {video['views']}")
            if len(data['videos']) > 5:
                print(f"  ... and {len(data['videos']) - 5} more")
        else:
            print(f"\n🎬 Videos Found: 0")
        
        if data.get('raw_json_data'):
            print(f"\n🔍 Deep Scrape Data:")
            print(f"  • JSON Type: {data['raw_json_data'].get('type', 'Unknown')}")
            print(f"  • JSON Data Size: {len(str(data['raw_json_data'])) / 1024:.2f} KB")
        
        if data.get('page_metadata'):
            meta = data['page_metadata']
            print(f"\n📄 Page Metadata:")
            print(f"  • Page Title: {meta.get('page_title', 'N/A')}")
            if meta.get('open_graph'):
                og = meta['open_graph']
                print(f"  • OG Title: {og.get('og:title', 'N/A')}")
                print(f"  • OG Description: {og.get('og:description', 'N/A')[:50]}..." if og.get('og:description') else "  • OG Description: N/A")
        
        print("\n" + "="*60)


def main():
    # Example usage
    username = ".wabby"  # Can be with or without @
    
    scraper = TikTokScraper(headless=False)  # Set to True for headless mode
    
    try:
        scraper.start()
        print("Starting deep scrape...")
        profile_data = scraper.scrape_profile(username, deep_scrape=True)
        
        # Print summary
        scraper.print_summary(profile_data)
        
        # Save to file
        scraper.save_to_file(profile_data, f'{username}_profile_deep.json')
        
        print(f"\n✅ Scraping complete! Check {username}_profile_deep.json for full data.")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()


