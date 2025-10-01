#!/usr/bin/env python3
"""
Ultimate TikTok Scraper
Intercepts network requests to capture API responses with video data
"""

import json
import time
import re
from playwright.sync_api import sync_playwright, Route
from datetime import datetime
from typing import Dict, List
import traceback


class UltimateTikTokScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        self.context = None
        self.captured_api_responses = []
        self.captured_videos = []
    
    def start(self):
        """Initialize browser with network interception"""
        self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = self.context.new_page()
        
        # Intercept API responses
        self.page.on("response", self._handle_response)
        
        print("✅ Browser initialized with network interception")
    
    def _handle_response(self, response):
        """Handle network responses"""
        try:
            url = response.url
            
            # Look for API calls that might contain video data
            if any(keyword in url for keyword in ['/api/', '/video/', '/item/', '/post/', '/aweme/']):
                try:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'json' in content_type:
                            try:
                                data = response.json()
                                self.captured_api_responses.append({
                                    'url': url,
                                    'data': data,
                                    'timestamp': datetime.now().isoformat()
                                })
                                
                                print(f"  📡 Captured API response: {url[:80]}...")
                                
                                # Try to extract videos from this response
                                videos = self._extract_videos_from_api_response(data)
                                if videos:
                                    print(f"     ✓ Found {len(videos)} videos in response")
                                    self.captured_videos.extend(videos)
                            
                            except:
                                pass
                except:
                    pass
        except:
            pass
    
    def _extract_videos_from_api_response(self, data: Dict) -> List[Dict]:
        """Extract video data from API response"""
        videos = []
        
        try:
            # Try different common structures
            if isinstance(data, dict):
                # Pattern 1: itemList
                if 'itemList' in data:
                    for item in data['itemList']:
                        video = self._parse_video_item(item)
                        if video:
                            videos.append(video)
                
                # Pattern 2: items
                if 'items' in data:
                    for item in data['items']:
                        video = self._parse_video_item(item)
                        if video:
                            videos.append(video)
                
                # Pattern 3: data.itemList
                if 'data' in data and isinstance(data['data'], dict):
                    if 'itemList' in data['data']:
                        for item in data['data']['itemList']:
                            video = self._parse_video_item(item)
                            if video:
                                videos.append(video)
                
                # Pattern 4: aweme_list
                if 'aweme_list' in data:
                    for item in data['aweme_list']:
                        video = self._parse_video_item(item)
                        if video:
                            videos.append(video)
                
                # Recursive search for video IDs
                videos.extend(self._recursive_video_search(data))
        
        except:
            pass
        
        return videos
    
    def _recursive_video_search(self, obj, depth=0, max_depth=5) -> List[Dict]:
        """Recursively search for video data in nested structures"""
        videos = []
        
        if depth > max_depth:
            return videos
        
        try:
            if isinstance(obj, dict):
                # Check if this looks like a video object
                if 'id' in obj and ('desc' in obj or 'video' in obj or 'stats' in obj):
                    video = self._parse_video_item(obj)
                    if video:
                        videos.append(video)
                
                # Recurse into nested objects
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        videos.extend(self._recursive_video_search(value, depth + 1, max_depth))
            
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        videos.extend(self._recursive_video_search(item, depth + 1, max_depth))
        
        except:
            pass
        
        return videos
    
    def _parse_video_item(self, item: Dict) -> Dict:
        """Parse video item data"""
        try:
            if not isinstance(item, dict):
                return None
            
            video = {}
            
            # ID
            video['id'] = item.get('id')
            if not video['id']:
                return None
            
            # Description
            video['desc'] = item.get('desc') or item.get('description')
            
            # Create time
            video['create_time'] = item.get('createTime') or item.get('create_time')
            
            # Author
            if 'author' in item:
                author = item['author']
                video['author'] = {
                    'id': author.get('id'),
                    'unique_id': author.get('uniqueId') or author.get('unique_id'),
                    'nickname': author.get('nickname'),
                    'avatar': author.get('avatarLarger') or author.get('avatarMedium') or author.get('avatar')
                }
            
            # Stats
            if 'stats' in item:
                stats = item['stats']
                video['stats'] = {
                    'play_count': stats.get('playCount') or stats.get('play_count') or 0,
                    'digg_count': stats.get('diggCount') or stats.get('digg_count') or 0,
                    'comment_count': stats.get('commentCount') or stats.get('comment_count') or 0,
                    'share_count': stats.get('shareCount') or stats.get('share_count') or 0
                }
            
            # Video details
            if 'video' in item:
                vid = item['video']
                video['video'] = {
                    'duration': vid.get('duration'),
                    'cover': vid.get('cover') or vid.get('dynamicCover'),
                    'play_addr': vid.get('playAddr'),
                    'download_addr': vid.get('downloadAddr'),
                    'width': vid.get('width'),
                    'height': vid.get('height')
                }
            
            # Music
            if 'music' in item:
                music = item['music']
                video['music'] = {
                    'id': music.get('id'),
                    'title': music.get('title'),
                    'author': music.get('authorName')
                }
            
            # Hashtags/Challenges
            if 'challenges' in item or 'textExtra' in item:
                hashtags = []
                if 'challenges' in item:
                    hashtags = [ch.get('title') for ch in item['challenges'] if ch.get('title')]
                if 'textExtra' in item:
                    hashtags.extend([t.get('hashtagName') for t in item['textExtra'] if t.get('hashtagName')])
                video['hashtags'] = hashtags
            
            # Generate URL
            if video.get('author') and video['author'].get('unique_id'):
                video['url'] = f"https://www.tiktok.com/@{video['author']['unique_id']}/video/{video['id']}"
            else:
                video['url'] = f"https://www.tiktok.com/video/{video['id']}"
            
            return video
        
        except:
            return None
    
    def scrape_profile_ultimate(self, username: str) -> Dict:
        """Ultimate comprehensive scrape"""
        username = username.strip().lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        print(f"\n{'='*70}")
        print(f"🚀 ULTIMATE SCRAPE: @{username}")
        print(f"{'='*70}\n")
        
        profile_data = {
            'username': username,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'account_info': {},
            'statistics': {},
            'videos': [],
            'liked_videos': [],
            'api_responses_captured': 0
        }
        
        try:
            # Navigate and wait
            print(f"📍 Navigating to {url}...")
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            print("⏳ Waiting for API calls...")
            time.sleep(5)
            
            # Extract basic info
            print("\n📊 Extracting profile data...")
            profile_data['account_info'] = self._extract_basic_info()
            profile_data['statistics'] = self._extract_stats_from_page()
            
            # Aggressive scrolling to trigger more API calls
            print("\n📜 Scrolling to trigger video loading...")
            for i in range(15):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
                
                if (i + 1) % 5 == 0:
                    print(f"   Scroll {i+1}/15: {len(self.captured_videos)} videos captured so far...")
            
            # Try clicking on Videos tab explicitly
            print("\n🎬 Attempting to click Videos tab...")
            try:
                # Try multiple selectors for Videos tab
                video_tab_selectors = [
                    'a[href*="/video"]',
                    'div[role="tab"]:has-text("Videos")',
                    'a:has-text("Videos")'
                ]
                
                for selector in video_tab_selectors:
                    try:
                        self.page.click(selector, timeout=3000)
                        print(f"   ✓ Clicked Videos tab")
                        time.sleep(3)
                        break
                    except:
                        continue
            except:
                print("   ⚠️  Could not click Videos tab")
            
            # More scrolling after clicking
            print("\n📜 Additional scrolling...")
            for i in range(10):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
            
            print(f"\n⏳ Final wait for any remaining API calls...")
            time.sleep(3)
            
            # Try liked videos
            print("\n❤️  Attempting to scrape liked videos...")
            try:
                liked_url = f"https://www.tiktok.com/@{username}/liked"
                self.page.goto(liked_url, wait_until="networkidle", timeout=15000)
                time.sleep(3)
                
                # Check if private
                page_text = self.page.evaluate("document.body.innerText")
                if "private" not in page_text.lower():
                    print("   📜 Scrolling liked videos...")
                    for i in range(10):
                        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(1.5)
                else:
                    print("   🔒 Liked videos are private")
            except:
                print("   ⚠️  Could not access liked videos")
            
            # Compile results
            print(f"\n📦 Compiling results...")
            
            # Deduplicate videos
            unique_videos = {}
            for video in self.captured_videos:
                if video.get('id'):
                    unique_videos[video['id']] = video
            
            profile_data['videos'] = list(unique_videos.values())
            profile_data['api_responses_captured'] = len(self.captured_api_responses)
            
            # Take screenshots
            self.page.screenshot(path=f"{username}_ultimate.png", full_page=True)
            print(f"📸 Screenshot saved")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            traceback.print_exc()
            profile_data['error'] = str(e)
        
        return profile_data
    
    def _extract_basic_info(self) -> Dict:
        """Extract basic account info"""
        info = {}
        
        try:
            info['display_name'] = self.page.locator('h1').first.inner_text(timeout=3000)
        except:
            info['display_name'] = None
        
        try:
            info['bio'] = self.page.locator('h2[data-e2e="user-bio"]').first.inner_text(timeout=3000)
        except:
            info['bio'] = None
        
        return info
    
    def _extract_stats_from_page(self) -> Dict:
        """Extract statistics from page"""
        stats = {}
        
        try:
            # Try to get from JSON
            page_content = self.page.content()
            match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', page_content, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                user_detail = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
                user_info = user_detail.get('userInfo', {})
                
                user = user_info.get('user', {})
                stats['user_id'] = user.get('id')
                stats['nickname'] = user.get('nickname')
                
                user_stats = user_info.get('stats', {})
                stats['follower_count'] = user_stats.get('followerCount', 0)
                stats['following_count'] = user_stats.get('followingCount', 0)
                stats['heart_count'] = user_stats.get('heartCount', 0)
                stats['video_count'] = user_stats.get('videoCount', 0)
        except:
            pass
        
        return stats
    
    def close(self):
        """Close browser"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def save_results(self, data: Dict, username: str):
        """Save all results"""
        # Save main data
        main_file = f"{username}_ultimate.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        import os
        size = os.path.getsize(main_file) / 1024
        print(f"\n💾 Main data saved: {main_file} ({size:.1f} KB)")
        
        # Save videos separately
        if data.get('videos'):
            videos_file = f"{username}_videos.json"
            with open(videos_file, 'w', encoding='utf-8') as f:
                json.dump(data['videos'], f, indent=2, ensure_ascii=False)
            print(f"💾 Videos saved: {videos_file}")
        
        # Save API responses for debugging
        if self.captured_api_responses:
            api_file = f"{username}_api_responses.json"
            with open(api_file, 'w', encoding='utf-8') as f:
                json.dump(self.captured_api_responses, f, indent=2, ensure_ascii=False)
            print(f"💾 API responses saved: {api_file}")
    
    def print_summary(self, data: Dict):
        """Print summary"""
        print(f"\n{'='*70}")
        print("📊 ULTIMATE SCRAPE SUMMARY")
        print("="*70)
        
        print(f"\n👤 Profile: @{data['username']}")
        
        if data.get('statistics'):
            stats = data['statistics']
            print(f"\n📈 Statistics:")
            print(f"   Followers: {stats.get('follower_count', 'N/A'):,}")
            print(f"   Following: {stats.get('following_count', 'N/A'):,}")
            print(f"   Total Likes: {stats.get('heart_count', 'N/A'):,}")
            print(f"   Expected Videos: {stats.get('video_count', 'N/A')}")
        
        print(f"\n🎬 Videos Captured: {len(data.get('videos', []))}")
        
        if data.get('videos'):
            print(f"\n📹 Sample Videos:")
            for i, video in enumerate(data['videos'][:5], 1):
                print(f"\n   {i}. {video.get('url')}")
                print(f"      Description: {video.get('desc', 'N/A')[:60]}...")
                if video.get('stats'):
                    s = video['stats']
                    print(f"      Stats: 👁️  {s.get('play_count', 0):,} | "
                          f"❤️  {s.get('digg_count', 0):,} | "
                          f"💬 {s.get('comment_count', 0):,}")
            
            if len(data['videos']) > 5:
                print(f"\n   ... and {len(data['videos']) - 5} more videos")
        
        print(f"\n📡 API Responses Captured: {data.get('api_responses_captured', 0)}")
        print(f"\n{'='*70}")


def main():
    username = ".wabby"
    
    scraper = UltimateTikTokScraper(headless=False)
    
    try:
        scraper.start()
        
        # Perform ultimate scrape
        data = scraper.scrape_profile_ultimate(username)
        
        # Print summary
        scraper.print_summary(data)
        
        # Save results
        scraper.save_results(data, username)
        
        print(f"\n✅ ULTIMATE SCRAPE COMPLETE!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

