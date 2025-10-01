#!/usr/bin/env python3
"""
Advanced TikTok Profile Scraper
Extracts comprehensive data including videos, likes, comments, and all activity
"""

import json
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
from typing import Dict, List, Optional
import traceback


class AdvancedTikTokScraper:
    def __init__(self, headless=False, slow_mo=100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.page = None
        self.context = None
    
    def start(self):
        """Initialize the browser with advanced settings"""
        self.playwright = sync_playwright().start()
        
        # Launch with more realistic browser settings
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Create context with realistic settings
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation']
        )
        
        self.page = self.context.new_page()
        
        # Add stealth modifications
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("✅ Browser initialized with stealth settings")
    
    def close(self):
        """Close the browser"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def scrape_profile_comprehensive(self, username: str) -> Dict:
        """
        Comprehensive scrape of TikTok profile
        
        Args:
            username: TikTok username (with or without @)
        
        Returns:
            Complete profile data dictionary
        """
        username = username.strip().lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        print(f"\n{'='*70}")
        print(f"🎯 Starting Comprehensive Scrape: @{username}")
        print(f"{'='*70}\n")
        
        profile_data = {
            'username': username,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'account_info': {},
            'statistics': {},
            'videos': [],
            'liked_videos': [],
            'raw_json_data': {},
            'page_metadata': {},
            'tabs_available': [],
            'scraping_log': []
        }
        
        try:
            # Navigate to profile
            print(f"📍 Navigating to {url}...")
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self._log(profile_data, "Navigated to profile page")
            
            # Wait for page to load
            time.sleep(5)
            
            # Take initial screenshot
            screenshot_path = f"{username}_initial.png"
            self.page.screenshot(path=screenshot_path, full_page=False)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Extract all available data from initial page
            print("\n📊 Extracting account information...")
            profile_data['account_info'] = self._extract_account_info()
            
            print("🔍 Extracting raw JSON data...")
            profile_data['raw_json_data'] = self._extract_all_json_data()
            
            print("📄 Extracting page metadata...")
            profile_data['page_metadata'] = self._extract_page_metadata()
            
            # Parse detailed stats from raw JSON
            print("📈 Parsing statistics from JSON...")
            profile_data['statistics'] = self._parse_statistics(profile_data['raw_json_data'])
            
            # Detect available tabs
            print("🔎 Detecting available tabs...")
            profile_data['tabs_available'] = self._detect_tabs()
            
            # Scrape Videos tab
            print("\n🎬 Scraping VIDEOS tab...")
            profile_data['videos'] = self._scrape_videos_tab(username)
            
            # Scrape Liked tab if available
            if 'Liked' in profile_data['tabs_available']:
                print("\n❤️  Scraping LIKED tab...")
                profile_data['liked_videos'] = self._scrape_liked_tab(username)
            else:
                print("⚠️  Liked tab not available (may be private)")
                self._log(profile_data, "Liked tab not accessible")
            
            # Try to get additional insights
            print("\n🔬 Extracting additional insights...")
            profile_data['additional_insights'] = self._extract_additional_insights()
            
            # Final full-page screenshot
            final_screenshot = f"{username}_final.png"
            self.page.screenshot(path=final_screenshot, full_page=True)
            print(f"📸 Final screenshot saved: {final_screenshot}")
            
            self._log(profile_data, "Scraping completed successfully")
            
        except Exception as e:
            error_msg = f"Error during scraping: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            self._log(profile_data, error_msg)
            profile_data['error'] = str(e)
        
        return profile_data
    
    def _log(self, profile_data: Dict, message: str):
        """Add log entry to profile data"""
        profile_data['scraping_log'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message
        })
    
    def _extract_account_info(self) -> Dict:
        """Extract visible account information"""
        info = {}
        
        # Try multiple selectors for each field
        selectors = {
            'display_name': ['h1[data-e2e="user-title"]', 'h1[class*="Title"]', 'h1'],
            'bio': ['h2[data-e2e="user-bio"]', 'h2[class*="Bio"]'],
            'followers': ['[data-e2e="followers-count"]', 'strong[title*="Followers"]'],
            'following': ['[data-e2e="following-count"]', 'strong[title*="Following"]'],
            'likes': ['[data-e2e="likes-count"]', 'strong[title*="Likes"]'],
            'verified': ['svg[data-e2e="verified-badge"]'],
            'avatar': ['img[data-e2e="user-avatar"]', 'img[class*="Avatar"]']
        }
        
        for field, selector_list in selectors.items():
            for selector in selector_list:
                try:
                    if field == 'verified':
                        info[field] = self.page.locator(selector).count() > 0
                        break
                    elif field == 'avatar':
                        element = self.page.locator(selector).first
                        info['avatar_url'] = element.get_attribute('src', timeout=3000)
                        break
                    else:
                        element = self.page.locator(selector).first
                        info[field] = element.inner_text(timeout=3000)
                        break
                except:
                    continue
            
            if field not in info and field != 'verified':
                info[field] = None
        
        if 'verified' not in info:
            info['verified'] = False
        
        return info
    
    def _extract_all_json_data(self) -> Dict:
        """Extract all embedded JSON data structures"""
        all_json = {}
        
        try:
            page_content = self.page.content()
            
            # Pattern 1: SIGI_STATE
            sigi_pattern = r'<script id="SIGI_STATE"[^>]*>(.*?)</script>'
            sigi_match = re.search(sigi_pattern, page_content, re.DOTALL)
            if sigi_match:
                try:
                    all_json['SIGI_STATE'] = json.loads(sigi_match.group(1))
                    print("  ✓ Found SIGI_STATE")
                except:
                    pass
            
            # Pattern 2: __UNIVERSAL_DATA_FOR_REHYDRATION__
            universal_pattern = r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>'
            universal_match = re.search(universal_pattern, page_content, re.DOTALL)
            if universal_match:
                try:
                    all_json['UNIVERSAL_DATA'] = json.loads(universal_match.group(1))
                    print("  ✓ Found UNIVERSAL_DATA")
                except:
                    pass
            
            # Pattern 3: __NEXT_DATA__ (if using Next.js)
            next_pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            next_match = re.search(next_pattern, page_content, re.DOTALL)
            if next_match:
                try:
                    all_json['NEXT_DATA'] = json.loads(next_match.group(1))
                    print("  ✓ Found NEXT_DATA")
                except:
                    pass
            
            # Pattern 4: JSON-LD
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, page_content, re.DOTALL)
            if json_ld_matches:
                all_json['JSON_LD'] = []
                for match in json_ld_matches:
                    try:
                        all_json['JSON_LD'].append(json.loads(match))
                    except:
                        pass
                print(f"  ✓ Found {len(all_json['JSON_LD'])} JSON-LD blocks")
            
        except Exception as e:
            print(f"  ⚠️  Error extracting JSON: {e}")
        
        return all_json
    
    def _parse_statistics(self, raw_json: Dict) -> Dict:
        """Parse detailed statistics from raw JSON"""
        stats = {}
        
        try:
            if 'UNIVERSAL_DATA' in raw_json:
                user_detail = raw_json['UNIVERSAL_DATA'].get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
                
                if 'userInfo' in user_detail:
                    user_info = user_detail['userInfo']
                    
                    # Get user data
                    user = user_info.get('user', {})
                    stats['user_id'] = user.get('id')
                    stats['unique_id'] = user.get('uniqueId')
                    stats['nickname'] = user.get('nickname')
                    stats['signature'] = user.get('signature')
                    stats['verified'] = user.get('verified', False)
                    stats['private_account'] = user.get('privateAccount', False)
                    stats['secret'] = user.get('secret', False)
                    stats['avatar_larger'] = user.get('avatarLarger')
                    stats['avatar_medium'] = user.get('avatarMedium')
                    stats['avatar_thumb'] = user.get('avatarThumb')
                    
                    # Get stats
                    user_stats = user_info.get('stats', {})
                    stats['follower_count'] = user_stats.get('followerCount', 0)
                    stats['following_count'] = user_stats.get('followingCount', 0)
                    stats['heart_count'] = user_stats.get('heartCount', 0)
                    stats['video_count'] = user_stats.get('videoCount', 0)
                    stats['digg_count'] = user_stats.get('diggCount', 0)
                    stats['friend_count'] = user_stats.get('friendCount', 0)
                    
                    print(f"  ✓ Parsed: {stats['video_count']} videos, {stats['follower_count']} followers")
        
        except Exception as e:
            print(f"  ⚠️  Error parsing statistics: {e}")
        
        return stats
    
    def _extract_page_metadata(self) -> Dict:
        """Extract page metadata"""
        metadata = {}
        
        try:
            metadata['title'] = self.page.title()
            
            # Meta tags
            meta_tags = {}
            for meta in self.page.locator('meta').all()[:100]:
                try:
                    name = meta.get_attribute('name') or meta.get_attribute('property')
                    content = meta.get_attribute('content')
                    if name and content:
                        meta_tags[name] = content
                except:
                    pass
            
            metadata['meta_tags'] = meta_tags
            
        except Exception as e:
            print(f"  ⚠️  Error extracting metadata: {e}")
        
        return metadata
    
    def _detect_tabs(self) -> List[str]:
        """Detect available tabs on the profile"""
        tabs = []
        
        try:
            # Look for tab elements
            tab_selectors = [
                '[data-e2e="user-tabs"] a',
                'div[role="tablist"] a',
                'a[role="tab"]',
                'div[class*="Tab"] a'
            ]
            
            for selector in tab_selectors:
                try:
                    tab_elements = self.page.locator(selector).all()
                    if tab_elements:
                        for tab in tab_elements:
                            try:
                                text = tab.inner_text(timeout=1000)
                                if text and text not in tabs:
                                    tabs.append(text)
                            except:
                                pass
                        break
                except:
                    continue
            
            if tabs:
                print(f"  ✓ Found tabs: {', '.join(tabs)}")
            else:
                print(f"  ⚠️  No tabs detected")
        
        except Exception as e:
            print(f"  ⚠️  Error detecting tabs: {e}")
        
        return tabs
    
    def _scrape_videos_tab(self, username: str) -> List[Dict]:
        """Scrape videos from the Videos tab"""
        videos = []
        
        try:
            # Make sure we're on the Videos tab
            url = f"https://www.tiktok.com/@{username}"
            if self.page.url != url:
                self.page.goto(url, wait_until="domcontentloaded")
                time.sleep(3)
            
            # Scroll to load videos
            print("  📜 Scrolling to load videos...")
            videos = self._scroll_and_extract_videos(max_scrolls=10)
            
            print(f"  ✓ Extracted {len(videos)} videos")
            
        except Exception as e:
            print(f"  ❌ Error scraping videos: {e}")
            traceback.print_exc()
        
        return videos
    
    def _scrape_liked_tab(self, username: str) -> List[Dict]:
        """Scrape videos from the Liked tab"""
        liked_videos = []
        
        try:
            # Navigate to liked tab
            liked_url = f"https://www.tiktok.com/@{username}/liked"
            print(f"  📍 Navigating to {liked_url}")
            self.page.goto(liked_url, wait_until="domcontentloaded")
            time.sleep(3)
            
            # Check if liked videos are visible
            page_content = self.page.content()
            if "This user's liked videos are private" in page_content or "private" in page_content.lower():
                print("  🔒 Liked videos are private")
                return []
            
            # Scroll to load liked videos
            print("  📜 Scrolling to load liked videos...")
            liked_videos = self._scroll_and_extract_videos(max_scrolls=10)
            
            print(f"  ✓ Extracted {len(liked_videos)} liked videos")
            
        except Exception as e:
            print(f"  ⚠️  Error scraping liked videos: {e}")
        
        return liked_videos
    
    def _scroll_and_extract_videos(self, max_scrolls: int = 10) -> List[Dict]:
        """Scroll through page and extract all video data"""
        videos = []
        video_urls_seen = set()
        
        try:
            for scroll_num in range(max_scrolls):
                # Scroll down
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                
                # Extract video elements
                video_selectors = [
                    '[data-e2e="user-post-item"]',
                    'div[class*="DivItemContainer"]',
                    'a[href*="/video/"]'
                ]
                
                for selector in video_selectors:
                    try:
                        elements = self.page.locator(selector).all()
                        
                        for element in elements:
                            try:
                                video_data = self._extract_video_data(element)
                                
                                if video_data and video_data.get('url'):
                                    if video_data['url'] not in video_urls_seen:
                                        video_urls_seen.add(video_data['url'])
                                        videos.append(video_data)
                            except:
                                continue
                        
                        if elements:
                            break
                    except:
                        continue
                
                # Check if we've reached the bottom
                is_at_bottom = self.page.evaluate("""
                    () => {
                        return (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 100;
                    }
                """)
                
                if scroll_num % 3 == 0:
                    print(f"    Scroll {scroll_num + 1}/{max_scrolls}: Found {len(videos)} unique videos so far...")
                
                if is_at_bottom and scroll_num > 3:
                    print(f"    Reached bottom of page")
                    break
        
        except Exception as e:
            print(f"  ⚠️  Error during scrolling: {e}")
        
        return videos
    
    def _extract_video_data(self, element) -> Optional[Dict]:
        """Extract detailed data from a video element"""
        video_data = {}
        
        try:
            # Get URL
            try:
                href = element.get_attribute('href', timeout=1000)
                if not href:
                    href = element.locator('a').first.get_attribute('href', timeout=1000)
                
                if href:
                    if href.startswith('/'):
                        video_data['url'] = f"https://www.tiktok.com{href}"
                    else:
                        video_data['url'] = href
                    
                    # Extract video ID from URL
                    video_id_match = re.search(r'/video/(\d+)', href)
                    if video_id_match:
                        video_data['video_id'] = video_id_match.group(1)
            except:
                pass
            
            # Get thumbnail
            try:
                img = element.locator('img').first
                video_data['thumbnail'] = img.get_attribute('src', timeout=1000)
                video_data['description'] = img.get_attribute('alt', timeout=1000)
            except:
                pass
            
            # Get view count
            try:
                view_selectors = ['[data-e2e="video-views"]', 'strong', 'span[class*="view"]']
                for selector in view_selectors:
                    try:
                        views = element.locator(selector).first.inner_text(timeout=1000)
                        if views:
                            video_data['views'] = views
                            break
                    except:
                        continue
            except:
                pass
            
            # Get duration if visible
            try:
                duration = element.locator('[class*="duration"]').first.inner_text(timeout=1000)
                video_data['duration'] = duration
            except:
                pass
            
        except:
            pass
        
        return video_data if video_data.get('url') else None
    
    def _extract_additional_insights(self) -> Dict:
        """Extract any additional insights from the page"""
        insights = {}
        
        try:
            # Try to find any additional data in the page
            page_text = self.page.evaluate("document.body.innerText")
            
            # Check for specific indicators
            insights['page_has_content'] = len(page_text) > 100
            insights['page_length'] = len(page_text)
            
            # Count links
            all_links = self.page.locator('a').all()
            insights['total_links'] = len(all_links)
            
            # Count images
            all_images = self.page.locator('img').all()
            insights['total_images'] = len(all_images)
            
        except Exception as e:
            print(f"  ⚠️  Error extracting insights: {e}")
        
        return insights
    
    def save_to_file(self, data: Dict, filename: str):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        import os
        file_size = os.path.getsize(filename)
        size_mb = file_size / (1024 * 1024)
        
        print(f"\n💾 Data saved to: {filename}")
        print(f"📦 File size: {size_mb:.2f} MB")
    
    def print_comprehensive_summary(self, data: Dict):
        """Print detailed summary of all scraped data"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE SCRAPING SUMMARY")
        print("="*70)
        
        print(f"\n👤 PROFILE: @{data['username']}")
        print(f"🔗 URL: {data['url']}")
        print(f"⏰ Scraped: {data['scraped_at']}")
        
        # Account Info
        if data.get('account_info'):
            info = data['account_info']
            print(f"\n📝 ACCOUNT INFO:")
            print(f"  • Display Name: {info.get('display_name', 'N/A')}")
            print(f"  • Bio: {info.get('bio', 'N/A')}")
            print(f"  • Verified: {'✓' if info.get('verified') else '✗'}")
        
        # Statistics
        if data.get('statistics'):
            stats = data['statistics']
            print(f"\n📈 STATISTICS:")
            print(f"  • User ID: {stats.get('user_id', 'N/A')}")
            print(f"  • Followers: {stats.get('follower_count', 'N/A'):,}")
            print(f"  • Following: {stats.get('following_count', 'N/A'):,}")
            print(f"  • Total Likes: {stats.get('heart_count', 'N/A'):,}")
            print(f"  • Video Count: {stats.get('video_count', 'N/A')}")
            print(f"  • Friend Count: {stats.get('friend_count', 'N/A')}")
            print(f"  • Private Account: {'Yes' if stats.get('private_account') else 'No'}")
        
        # Videos
        print(f"\n🎬 VIDEOS SCRAPED: {len(data.get('videos', []))}")
        if data.get('videos'):
            for i, video in enumerate(data['videos'][:5], 1):
                print(f"  {i}. {video.get('url', 'N/A')}")
                if video.get('views'):
                    print(f"     👁️  {video['views']} views")
                if video.get('description'):
                    desc = video['description'][:60]
                    print(f"     📝 {desc}...")
            
            if len(data['videos']) > 5:
                print(f"  ... and {len(data['videos']) - 5} more videos")
        
        # Liked Videos
        print(f"\n❤️  LIKED VIDEOS SCRAPED: {len(data.get('liked_videos', []))}")
        if data.get('liked_videos'):
            for i, video in enumerate(data['liked_videos'][:3], 1):
                print(f"  {i}. {video.get('url', 'N/A')}")
        
        # Available Tabs
        if data.get('tabs_available'):
            print(f"\n📑 TABS DETECTED: {', '.join(data['tabs_available'])}")
        
        # Raw Data
        if data.get('raw_json_data'):
            json_types = list(data['raw_json_data'].keys())
            print(f"\n🔍 RAW JSON DATA CAPTURED:")
            for jtype in json_types:
                size = len(json.dumps(data['raw_json_data'][jtype]))
                print(f"  • {jtype}: {size / 1024:.1f} KB")
        
        # Insights
        if data.get('additional_insights'):
            insights = data['additional_insights']
            print(f"\n💡 ADDITIONAL INSIGHTS:")
            print(f"  • Total Links: {insights.get('total_links', 0)}")
            print(f"  • Total Images: {insights.get('total_images', 0)}")
        
        # Scraping Log
        if data.get('scraping_log'):
            print(f"\n📋 SCRAPING LOG ({len(data['scraping_log'])} entries):")
            for log in data['scraping_log'][-3:]:
                print(f"  • {log['message']}")
        
        print("\n" + "="*70)


def main():
    """Main execution"""
    username = ".wabby"
    
    print("🚀 Advanced TikTok Scraper")
    print("="*70)
    
    scraper = AdvancedTikTokScraper(headless=False, slow_mo=50)
    
    try:
        scraper.start()
        
        # Perform comprehensive scrape
        profile_data = scraper.scrape_profile_comprehensive(username)
        
        # Print summary
        scraper.print_comprehensive_summary(profile_data)
        
        # Save to file
        filename = f"{username}_comprehensive.json"
        scraper.save_to_file(profile_data, filename)
        
        print(f"\n✅ SCRAPING COMPLETE!")
        print(f"📁 Check {filename} for all data")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

