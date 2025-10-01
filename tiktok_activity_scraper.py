#!/usr/bin/env python3
"""
TikTok Complete Activity Scraper
Captures ALL activity: videos, comments, likes, followers, duets, patterns
"""

import json
import time
import re
from playwright.sync_api import sync_playwright
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import traceback


class TikTokActivityScraper:
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
        self.page.on("response", self._handle_response)
        
        print("✅ Browser initialized with network interception")
    
    def scrape_complete_activity(self, username: str) -> Dict:
        """
        Comprehensive activity scrape - everything!
        """
        username = username.strip().lstrip('@')
        
        print(f"\n{'='*70}")
        print(f"🎯 COMPLETE ACTIVITY SCRAPE: @{username}")
        print(f"{'='*70}\n")
        
        activity_data = {
            'username': username,
            'url': f"https://www.tiktok.com/@{username}",
            'scraped_at': datetime.now().isoformat(),
            'profile': {},
            'statistics': {},
            'videos': [],
            'liked_videos': {},
            'comments_made': [],
            'social_connections': {},
            'duets_stitches': {},
            'activity_analysis': {},
            'engagement_patterns': {}
        }
        
        try:
            # Step 1: Basic profile and videos
            print("📊 Step 1/6: Scraping profile and videos...")
            self._navigate_and_scrape_videos(username, activity_data)
            print(f"   ✓ Found {len(activity_data['videos'])} videos")
            
            # Step 2: Liked videos
            print("\n❤️  Step 2/6: Scraping liked videos...")
            activity_data['liked_videos'] = self._scrape_liked_videos(username)
            
            # Step 3: Comments
            print("\n💬 Step 3/6: Scraping comments...")
            activity_data['comments_made'] = self._scrape_user_comments(username, activity_data['videos'])
            print(f"   ✓ Found {len(activity_data['comments_made'])} comments")
            
            # Step 4: Social connections
            print("\n👥 Step 4/6: Scraping followers/following...")
            activity_data['social_connections'] = self._scrape_social_connections(username)
            
            # Step 5: Duets and stitches
            print("\n🎭 Step 5/6: Finding duets/stitches...")
            activity_data['duets_stitches'] = self._find_duets_stitches(username)
            
            # Step 6: Analyze patterns
            print("\n📈 Step 6/6: Analyzing activity patterns...")
            activity_data['activity_analysis'] = self._analyze_patterns(activity_data)
            activity_data['engagement_patterns'] = self._analyze_engagement(activity_data)
            
            # Screenshots
            self.page.screenshot(path=f"{username}_activity_final.png", full_page=True)
            print(f"\n📸 Screenshot saved: {username}_activity_final.png")
            
        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            traceback.print_exc()
            activity_data['error'] = str(e)
        
        return activity_data
    
    def _handle_response(self, response):
        """Intercept API responses"""
        try:
            url = response.url
            if any(kw in url for kw in ['/api/', '/aweme/', '/item_list', '/post/']):
                if response.status == 200:
                    try:
                        data = response.json()
                        self.captured_api_responses.append({'url': url, 'data': data})
                        
                        # Extract videos
                        videos = self._extract_videos_from_api(data)
                        if videos:
                            self.captured_videos.extend(videos)
                    except:
                        pass
        except:
            pass
    
    def _navigate_and_scrape_videos(self, username: str, activity_data: Dict):
        """Navigate to profile and scrape videos with network interception"""
        url = f"https://www.tiktok.com/@{username}"
        
        print(f"   📍 Navigating to profile...")
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        
        # Extract profile info and stats
        activity_data['profile'] = self._extract_profile_info()
        activity_data['statistics'] = self._extract_statistics()
        
        # Aggressive scrolling to load videos
        print(f"   📜 Scrolling to load videos...")
        for i in range(15):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5)
            
            if (i + 1) % 5 == 0:
                print(f"      Scroll {i+1}/15: {len(self.captured_videos)} videos captured...")
        
        # Try clicking Videos tab
        try:
            self.page.click('a[href*="/video"]', timeout=3000)
            time.sleep(3)
            
            # More scrolling
            for i in range(10):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
        except:
            pass
        
        # Deduplicate videos
        unique_videos = {v['id']: v for v in self.captured_videos if v.get('id')}
        activity_data['videos'] = list(unique_videos.values())
        
        # Filter to only user's videos
        user_videos = [v for v in activity_data['videos'] 
                       if v.get('author', {}).get('unique_id', '').lower() == username.lower()]
        activity_data['videos'] = user_videos
    
    def _extract_profile_info(self) -> Dict:
        """Extract basic profile info"""
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
    
    def _extract_statistics(self) -> Dict:
        """Extract statistics from embedded JSON"""
        stats = {}
        
        try:
            page_content = self.page.content()
            match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', 
                            page_content, re.DOTALL)
            
            if match:
                data = json.loads(match.group(1))
                user_detail = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
                user_info = user_detail.get('userInfo', {})
                
                user = user_info.get('user', {})
                stats['user_id'] = user.get('id')
                stats['unique_id'] = user.get('uniqueId')
                stats['nickname'] = user.get('nickname')
                stats['signature'] = user.get('signature')
                stats['verified'] = user.get('verified', False)
                stats['private_account'] = user.get('privateAccount', False)
                
                user_stats = user_info.get('stats', {})
                stats['follower_count'] = user_stats.get('followerCount', 0)
                stats['following_count'] = user_stats.get('followingCount', 0)
                stats['heart_count'] = user_stats.get('heartCount', 0)
                stats['video_count'] = user_stats.get('videoCount', 0)
                stats['friend_count'] = user_stats.get('friendCount', 0)
        except:
            pass
        
        return stats
    
    def _scrape_liked_videos(self, username: str) -> Dict:
        """Scrape liked videos comprehensively"""
        liked_url = f"https://www.tiktok.com/@{username}/liked"
        
        try:
            print(f"   📍 Navigating to liked tab...")
            self.page.goto(liked_url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(3)
            
            # Check if private
            page_text = self.page.evaluate("document.body.innerText").lower()
            if "private" in page_text:
                print(f"   🔒 Liked videos are private")
                return {'accessible': False, 'reason': 'Private', 'videos': []}
            
            # Reset captured videos
            liked_videos_start = len(self.captured_videos)
            
            # Aggressive scrolling
            print(f"   📜 Scrolling liked videos...")
            for i in range(20):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
                
                if (i + 1) % 10 == 0:
                    current_count = len(self.captured_videos) - liked_videos_start
                    print(f"      Scroll {i+1}/20: {current_count} liked videos...")
            
            # Get liked videos
            liked_videos = self.captured_videos[liked_videos_start:]
            unique_liked = {v['id']: v for v in liked_videos if v.get('id')}
            
            print(f"   ✓ Found {len(unique_liked)} liked videos")
            
            return {
                'accessible': True,
                'total_count': len(unique_liked),
                'videos': list(unique_liked.values())
            }
        
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            return {'accessible': False, 'reason': str(e), 'videos': []}
    
    def _scrape_user_comments(self, username: str, user_videos: List[Dict]) -> List[Dict]:
        """Scrape comments made by user"""
        comments = []
        
        print(f"   🔍 Checking {len(user_videos[:5])} videos for comments...")
        
        # Check first 5 videos for comments
        for i, video in enumerate(user_videos[:5], 1):
            if not video.get('url'):
                continue
            
            try:
                print(f"      Video {i}/5: {video['url'][:60]}...")
                video_comments = self._get_comments_from_video(video['url'], username)
                comments.extend(video_comments)
                
                if video_comments:
                    print(f"         ✓ Found {len(video_comments)} comments")
            except Exception as e:
                print(f"         ⚠️  Error: {e}")
                continue
        
        return comments
    
    def _get_comments_from_video(self, video_url: str, username: str) -> List[Dict]:
        """Get comments from a specific video"""
        comments = []
        
        try:
            self.page.goto(video_url, timeout=15000)
            time.sleep(3)
            
            # Try to expand comments
            try:
                comment_selectors = [
                    '[data-e2e="browse-comment"]',
                    'button:has-text("Comments")',
                    '[class*="comment"]'
                ]
                
                for selector in comment_selectors:
                    try:
                        self.page.click(selector, timeout=2000)
                        break
                    except:
                        continue
                
                time.sleep(2)
            except:
                pass
            
            # Scroll comments section
            for _ in range(5):
                try:
                    self.page.evaluate("""
                        document.querySelector('[data-e2e="comment-list"]')?.scrollTo(0, 999999)
                    """)
                    time.sleep(1)
                except:
                    break
            
            # Extract comments by this user
            comment_elements = self.page.locator('[data-e2e="comment-item"]').all()
            
            for element in comment_elements[:50]:  # Limit to first 50 comments
                try:
                    author_elem = element.locator('[data-e2e="comment-username"]')
                    author = author_elem.inner_text(timeout=1000)
                    
                    if author.lower().replace('@', '') == username.lower():
                        text_elem = element.locator('[data-e2e="comment-text"]')
                        text = text_elem.inner_text(timeout=1000)
                        
                        comment_data = {
                            'author': author,
                            'text': text,
                            'video_url': video_url,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Try to get comment likes
                        try:
                            likes_elem = element.locator('[data-e2e="comment-like-count"]')
                            likes = likes_elem.inner_text(timeout=1000)
                            comment_data['likes'] = likes
                        except:
                            comment_data['likes'] = '0'
                        
                        comments.append(comment_data)
                except:
                    continue
        
        except Exception as e:
            pass
        
        return comments
    
    def _scrape_social_connections(self, username: str) -> Dict:
        """Scrape followers and following lists"""
        social = {
            'followers': [],
            'following': [],
            'followers_accessible': False,
            'following_accessible': False
        }
        
        # Go back to profile
        profile_url = f"https://www.tiktok.com/@{username}"
        
        try:
            self.page.goto(profile_url, timeout=15000)
            time.sleep(3)
            
            # Try followers
            print(f"   👥 Attempting to access followers...")
            try:
                self.page.click('[data-e2e="followers-count"]', timeout=5000)
                time.sleep(2)
                
                if self.page.locator('[data-e2e="user-item"]').count() > 0:
                    social['followers_accessible'] = True
                    
                    # Scroll modal
                    for _ in range(15):
                        try:
                            self.page.evaluate("""
                                document.querySelector('[data-e2e="followers-container"]')?.scrollTo(0, 999999)
                            """)
                            time.sleep(0.8)
                        except:
                            break
                    
                    # Extract followers
                    follower_elements = self.page.locator('[data-e2e="user-item"]').all()
                    
                    for elem in follower_elements[:200]:  # Limit to 200
                        try:
                            username_elem = elem.locator('[data-e2e="user-username"]')
                            name_elem = elem.locator('[data-e2e="user-name"]')
                            
                            follower = {
                                'username': username_elem.inner_text(timeout=1000),
                                'display_name': name_elem.inner_text(timeout=1000),
                                'verified': elem.locator('svg[data-e2e="verified-badge"]').count() > 0
                            }
                            social['followers'].append(follower)
                        except:
                            continue
                    
                    print(f"      ✓ Captured {len(social['followers'])} followers")
                    
                    # Close modal
                    try:
                        self.page.click('[data-e2e="modal-close"]', timeout=2000)
                    except:
                        self.page.keyboard.press('Escape')
                    time.sleep(1)
            
            except Exception as e:
                print(f"      ⚠️  Could not access followers: {e}")
            
            # Try following
            print(f"   👥 Attempting to access following...")
            try:
                self.page.click('[data-e2e="following-count"]', timeout=5000)
                time.sleep(2)
                
                if self.page.locator('[data-e2e="user-item"]').count() > 0:
                    social['following_accessible'] = True
                    
                    # Scroll modal
                    for _ in range(15):
                        try:
                            self.page.evaluate("""
                                document.querySelector('[data-e2e="following-container"]')?.scrollTo(0, 999999)
                            """)
                            time.sleep(0.8)
                        except:
                            break
                    
                    # Extract following
                    following_elements = self.page.locator('[data-e2e="user-item"]').all()
                    
                    for elem in following_elements[:200]:  # Limit to 200
                        try:
                            username_elem = elem.locator('[data-e2e="user-username"]')
                            name_elem = elem.locator('[data-e2e="user-name"]')
                            
                            following = {
                                'username': username_elem.inner_text(timeout=1000),
                                'display_name': name_elem.inner_text(timeout=1000),
                                'verified': elem.locator('svg[data-e2e="verified-badge"]').count() > 0
                            }
                            social['following'].append(following)
                        except:
                            continue
                    
                    print(f"      ✓ Captured {len(social['following'])} following")
            
            except Exception as e:
                print(f"      ⚠️  Could not access following: {e}")
        
        except Exception as e:
            print(f"   ⚠️  Error accessing social connections: {e}")
        
        return social
    
    def _find_duets_stitches(self, username: str) -> Dict:
        """Find duets and stitches"""
        results = {'duets': [], 'stitches': []}
        
        searches = [
            (f"duet with @{username}", 'duets'),
            (f"stitch with @{username}", 'stitches')
        ]
        
        for query, category in searches:
            try:
                print(f"   🔍 Searching: {query}")
                search_url = f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"
                
                self.page.goto(search_url, timeout=15000)
                time.sleep(3)
                
                # Scroll search results
                for _ in range(10):
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.5)
                
                # Count found videos from API responses
                found_count = len([v for v in self.captured_videos[-50:] 
                                 if v.get('desc') and query.lower() in v['desc'].lower()])
                
                print(f"      ✓ Found ~{found_count} {category}")
                
                # Store recent captures as duets/stitches
                recent = self.captured_videos[-50:]
                results[category] = [v for v in recent if v.get('id')]
                
            except Exception as e:
                print(f"      ⚠️  Error: {e}")
        
        return results
    
    def _analyze_patterns(self, activity_data: Dict) -> Dict:
        """Analyze activity patterns"""
        analysis = {
            'hashtag_usage': {},
            'music_usage': {},
            'video_count': len(activity_data['videos']),
            'liked_count': len(activity_data.get('liked_videos', {}).get('videos', [])),
            'comment_count': len(activity_data['comments_made'])
        }
        
        videos = activity_data['videos']
        
        if not videos:
            return analysis
        
        # Analyze hashtags
        all_hashtags = []
        for video in videos:
            if video.get('hashtags'):
                all_hashtags.extend(video['hashtags'])
        
        if all_hashtags:
            hashtag_counts = Counter(all_hashtags)
            analysis['hashtag_usage'] = dict(hashtag_counts.most_common(10))
        
        # Analyze music
        all_music = []
        for video in videos:
            if video.get('music') and video['music'].get('title'):
                all_music.append(video['music']['title'])
        
        if all_music:
            music_counts = Counter(all_music)
            analysis['music_usage'] = dict(music_counts.most_common(10))
        
        return analysis
    
    def _analyze_engagement(self, activity_data: Dict) -> Dict:
        """Analyze engagement patterns"""
        engagement = {}
        
        videos = activity_data['videos']
        
        if not videos:
            return engagement
        
        # Calculate averages
        total_views = sum(v.get('stats', {}).get('play_count', 0) for v in videos)
        total_likes = sum(v.get('stats', {}).get('digg_count', 0) for v in videos)
        total_comments = sum(v.get('stats', {}).get('comment_count', 0) for v in videos)
        total_shares = sum(v.get('stats', {}).get('share_count', 0) for v in videos)
        
        count = len(videos)
        
        engagement['average_metrics'] = {
            'avg_views': total_views // count if count else 0,
            'avg_likes': total_likes // count if count else 0,
            'avg_comments': total_comments // count if count else 0,
            'avg_shares': total_shares // count if count else 0
        }
        
        # Engagement rate
        if total_views > 0:
            engagement['engagement_rate'] = round((total_likes / total_views) * 100, 2)
        else:
            engagement['engagement_rate'] = 0
        
        # Best performing video
        if videos:
            best = max(videos, key=lambda v: v.get('stats', {}).get('play_count', 0))
            engagement['best_performing_video'] = {
                'url': best.get('url'),
                'views': best.get('stats', {}).get('play_count', 0),
                'likes': best.get('stats', {}).get('digg_count', 0),
                'desc': best.get('desc', '')[:100]
            }
        
        return engagement
    
    def _extract_videos_from_api(self, data: Dict) -> List[Dict]:
        """Extract videos from API response"""
        videos = []
        
        try:
            if isinstance(data, dict):
                if 'itemList' in data:
                    for item in data['itemList']:
                        video = self._parse_video_item(item)
                        if video:
                            videos.append(video)
                
                if 'items' in data:
                    for item in data['items']:
                        video = self._parse_video_item(item)
                        if video:
                            videos.append(video)
                
                if 'data' in data and isinstance(data['data'], dict):
                    if 'itemList' in data['data']:
                        for item in data['data']['itemList']:
                            video = self._parse_video_item(item)
                            if video:
                                videos.append(video)
        except:
            pass
        
        return videos
    
    def _parse_video_item(self, item: Dict) -> Optional[Dict]:
        """Parse video item from API"""
        try:
            if not isinstance(item, dict):
                return None
            
            video = {}
            
            video['id'] = item.get('id')
            if not video['id']:
                return None
            
            video['desc'] = item.get('desc')
            video['create_time'] = item.get('createTime')
            
            if 'author' in item:
                author = item['author']
                video['author'] = {
                    'id': author.get('id'),
                    'unique_id': author.get('uniqueId'),
                    'nickname': author.get('nickname')
                }
            
            if 'stats' in item:
                stats = item['stats']
                video['stats'] = {
                    'play_count': stats.get('playCount', 0),
                    'digg_count': stats.get('diggCount', 0),
                    'comment_count': stats.get('commentCount', 0),
                    'share_count': stats.get('shareCount', 0)
                }
            
            if 'video' in item:
                vid = item['video']
                video['video'] = {
                    'duration': vid.get('duration'),
                    'cover': vid.get('cover')
                }
            
            if 'music' in item:
                music = item['music']
                video['music'] = {
                    'id': music.get('id'),
                    'title': music.get('title'),
                    'author': music.get('authorName')
                }
            
            if 'challenges' in item:
                video['hashtags'] = [ch.get('title') for ch in item['challenges'] if ch.get('title')]
            
            if video.get('author') and video['author'].get('unique_id'):
                video['url'] = f"https://www.tiktok.com/@{video['author']['unique_id']}/video/{video['id']}"
            
            return video
        except:
            return None
    
    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def save_activity_data(self, data: Dict, username: str):
        """Save all activity data"""
        # Main comprehensive file
        main_file = f"{username}_complete_activity.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        import os
        size = os.path.getsize(main_file) / 1024
        print(f"\n💾 Complete activity saved: {main_file} ({size:.1f} KB)")
        
        # Separate files for convenience
        if data.get('videos'):
            with open(f"{username}_videos_activity.json", 'w') as f:
                json.dump(data['videos'], f, indent=2)
            print(f"💾 Videos saved: {username}_videos_activity.json")
        
        if data.get('comments_made'):
            with open(f"{username}_comments.json", 'w') as f:
                json.dump(data['comments_made'], f, indent=2)
            print(f"💾 Comments saved: {username}_comments.json")
        
        if data.get('liked_videos', {}).get('videos'):
            with open(f"{username}_liked_videos.json", 'w') as f:
                json.dump(data['liked_videos']['videos'], f, indent=2)
            print(f"💾 Liked videos saved: {username}_liked_videos.json")
        
        if data.get('social_connections'):
            with open(f"{username}_social.json", 'w') as f:
                json.dump(data['social_connections'], f, indent=2)
            print(f"💾 Social connections saved: {username}_social.json")
    
    def print_comprehensive_summary(self, data: Dict):
        """Print detailed summary"""
        print(f"\n{'='*70}")
        print("📊 COMPLETE ACTIVITY SUMMARY")
        print("="*70)
        
        print(f"\n👤 Profile: @{data['username']}")
        
        if data.get('statistics'):
            s = data['statistics']
            print(f"\n📈 Statistics:")
            print(f"   User ID: {s.get('user_id', 'N/A')}")
            print(f"   Followers: {s.get('follower_count', 0):,}")
            print(f"   Following: {s.get('following_count', 0):,}")
            print(f"   Total Likes: {s.get('heart_count', 0):,}")
            print(f"   Video Count: {s.get('video_count', 0)}")
            print(f"   Private: {'Yes' if s.get('private_account') else 'No'}")
        
        print(f"\n🎬 Content Scraped:")
        print(f"   Videos Posted: {len(data.get('videos', []))}")
        print(f"   Liked Videos: {data.get('liked_videos', {}).get('total_count', 0)}")
        
        print(f"\n💬 Engagement:")
        print(f"   Comments Made: {len(data.get('comments_made', []))}")
        print(f"   Duets Found: {len(data.get('duets_stitches', {}).get('duets', []))}")
        print(f"   Stitches Found: {len(data.get('duets_stitches', {}).get('stitches', []))}")
        
        if data.get('social_connections'):
            sc = data['social_connections']
            print(f"\n👥 Social Connections:")
            print(f"   Followers Captured: {len(sc.get('followers', []))}")
            print(f"   Following Captured: {len(sc.get('following', []))}")
        
        if data.get('activity_analysis', {}).get('hashtag_usage'):
            print(f"\n🏷️  Top Hashtags:")
            for tag, count in list(data['activity_analysis']['hashtag_usage'].items())[:5]:
                print(f"   #{tag}: {count} times")
        
        if data.get('engagement_patterns', {}).get('average_metrics'):
            avg = data['engagement_patterns']['average_metrics']
            print(f"\n💡 Average Engagement:")
            print(f"   Views: {avg.get('avg_views', 0):,}")
            print(f"   Likes: {avg.get('avg_likes', 0):,}")
            print(f"   Comments: {avg.get('avg_comments', 0):,}")
            print(f"   Engagement Rate: {data['engagement_patterns'].get('engagement_rate', 0)}%")
        
        print(f"\n{'='*70}")


def main():
    username = ".wabby"
    
    print("🚀 TikTok Complete Activity Scraper")
    print("="*70)
    
    scraper = TikTokActivityScraper(headless=False)
    
    try:
        scraper.start()
        
        # Run complete activity scrape
        activity_data = scraper.scrape_complete_activity(username)
        
        # Print summary
        scraper.print_comprehensive_summary(activity_data)
        
        # Save all data
        scraper.save_activity_data(activity_data, username)
        
        print(f"\n✅ COMPLETE ACTIVITY SCRAPE FINISHED!")
        print(f"📁 Check {username}_complete_activity.json for all data")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()


