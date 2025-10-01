#!/usr/bin/env python3
"""
Instagram Profile Scraper
Captures all public data: profile, posts, engagement, hashtags, comments
Note: Liked posts are NOT public and cannot be scraped
"""

import json
import time
import re
from playwright.sync_api import sync_playwright
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import traceback


class InstagramScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        self.context = None
    
    def start(self):
        """Initialize browser"""
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
        
        print("✅ Browser initialized")
    
    def scrape_profile(self, username: str) -> Dict:
        """
        Comprehensive Instagram profile scrape
        """
        username = username.strip().lstrip('@')
        url = f"https://www.instagram.com/{username}/"
        
        print(f"\n{'='*70}")
        print(f"📸 INSTAGRAM PROFILE SCRAPE: @{username}")
        print(f"{'='*70}\n")
        
        profile_data = {
            'username': username,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'profile_info': {},
            'statistics': {},
            'posts': [],
            'hashtag_analysis': {},
            'engagement_metrics': {},
            'posting_patterns': {},
            'top_posts': [],
            'note': 'Liked posts are private and cannot be scraped'
        }
        
        try:
            # Navigate to profile
            print(f"📍 Step 1/5: Navigating to profile...")
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            
            # Handle login popup if it appears
            self._handle_popups()
            
            # Extract profile info
            print(f"📊 Step 2/5: Extracting profile information...")
            profile_data['profile_info'] = self._extract_profile_info()
            profile_data['statistics'] = self._extract_statistics()
            
            # Check if account is private
            if self._is_private_account():
                print(f"   🔒 Account is private - cannot access posts")
                profile_data['private_account'] = True
                profile_data['posts'] = []
            else:
                # Extract posts
                print(f"🎬 Step 3/5: Extracting posts...")
                profile_data['posts'] = self._extract_posts(username)
                print(f"   ✓ Found {len(profile_data['posts'])} posts")
            
            # Analyze data
            if profile_data['posts']:
                print(f"📈 Step 4/5: Analyzing patterns...")
                profile_data['hashtag_analysis'] = self._analyze_hashtags(profile_data['posts'])
                profile_data['engagement_metrics'] = self._analyze_engagement(profile_data['posts'])
                profile_data['posting_patterns'] = self._analyze_posting_patterns(profile_data['posts'])
                profile_data['top_posts'] = self._get_top_posts(profile_data['posts'])
            
            # Screenshot
            print(f"📸 Step 5/5: Taking screenshot...")
            self.page.screenshot(path=f"{username}_instagram.png", full_page=True)
            print(f"   ✓ Screenshot saved")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            traceback.print_exc()
            profile_data['error'] = str(e)
        
        return profile_data
    
    def _handle_popups(self):
        """Close any popups that might appear"""
        try:
            # Close "Turn on Notifications" popup
            close_buttons = [
                'button:has-text("Not Now")',
                'button:has-text("Not now")',
                '[aria-label="Close"]',
                'svg[aria-label="Close"]'
            ]
            
            for selector in close_buttons:
                try:
                    if self.page.locator(selector).count() > 0:
                        self.page.click(selector, timeout=2000)
                        time.sleep(1)
                except:
                    pass
        except:
            pass
    
    def _extract_profile_info(self) -> Dict:
        """Extract profile information"""
        info = {}
        
        try:
            # Try to get profile data from meta tags
            page_content = self.page.content()
            
            # Try JSON in script tags
            json_pattern = r'window\._sharedData\s*=\s*({.+?});</script>'
            json_match = re.search(json_pattern, page_content)
            
            if json_match:
                try:
                    shared_data = json.loads(json_match.group(1))
                    user_data = shared_data.get('entry_data', {}).get('ProfilePage', [{}])[0]
                    user_data = user_data.get('graphql', {}).get('user', {})
                    
                    if user_data:
                        info['full_name'] = user_data.get('full_name')
                        info['biography'] = user_data.get('biography')
                        info['external_url'] = user_data.get('external_url')
                        info['is_verified'] = user_data.get('is_verified', False)
                        info['is_business_account'] = user_data.get('is_business_account', False)
                        info['profile_pic_url'] = user_data.get('profile_pic_url_hd')
                except:
                    pass
            
            # Also try extracting from visible elements
            try:
                # Full name
                if not info.get('full_name'):
                    name_elem = self.page.locator('header section span').first
                    info['full_name'] = name_elem.inner_text(timeout=3000)
            except:
                pass
            
            try:
                # Bio
                if not info.get('biography'):
                    bio_elem = self.page.locator('header section span').nth(1)
                    info['biography'] = bio_elem.inner_text(timeout=3000)
            except:
                info['biography'] = None
            
            # Try meta tags
            try:
                meta_desc = self.page.locator('meta[property="og:description"]').get_attribute('content')
                if meta_desc and not info.get('biography'):
                    # Format: "XX Followers, XX Following, XX Posts - See Instagram photos..."
                    parts = meta_desc.split(' - ')
                    if len(parts) > 1:
                        info['biography'] = ' - '.join(parts[1:])
            except:
                pass
            
        except Exception as e:
            print(f"   ⚠️  Error extracting profile info: {e}")
        
        return info
    
    def _extract_statistics(self) -> Dict:
        """Extract follower, following, posts counts"""
        stats = {}
        
        try:
            # Try to get from meta description
            meta_desc = self.page.locator('meta[property="og:description"]').get_attribute('content')
            
            if meta_desc:
                # Parse: "XX Followers, XX Following, XX Posts"
                followers_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta_desc, re.IGNORECASE)
                following_match = re.search(r'([\d,\.]+[KMB]?)\s+Following', meta_desc, re.IGNORECASE)
                posts_match = re.search(r'([\d,\.]+[KMB]?)\s+Posts', meta_desc, re.IGNORECASE)
                
                if followers_match:
                    stats['followers'] = followers_match.group(1)
                if following_match:
                    stats['following'] = following_match.group(1)
                if posts_match:
                    stats['posts'] = posts_match.group(1)
            
            # Also try from visible page elements
            stat_elements = self.page.locator('header section ul li').all()
            
            for i, elem in enumerate(stat_elements[:3]):
                try:
                    text = elem.inner_text(timeout=2000)
                    
                    if i == 0:  # Posts
                        if not stats.get('posts'):
                            stats['posts'] = text.split('\n')[0]
                    elif i == 1:  # Followers
                        if not stats.get('followers'):
                            stats['followers'] = text.split('\n')[0]
                    elif i == 2:  # Following
                        if not stats.get('following'):
                            stats['following'] = text.split('\n')[0]
                except:
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Error extracting statistics: {e}")
        
        return stats
    
    def _is_private_account(self) -> bool:
        """Check if account is private"""
        try:
            page_text = self.page.content().lower()
            return 'this account is private' in page_text
        except:
            return False
    
    def _extract_posts(self, username: str) -> List[Dict]:
        """Extract all visible posts"""
        posts = []
        
        try:
            # Scroll to load more posts
            print(f"   📜 Scrolling to load posts...")
            for i in range(10):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                
                if (i + 1) % 3 == 0:
                    print(f"      Scroll {i+1}/10...")
            
            # Find all post links
            post_links = []
            
            # Try multiple selectors
            link_selectors = [
                'article a[href*="/p/"]',
                'a[href*="/p/"]',
                'a[href*="/reel/"]'
            ]
            
            for selector in link_selectors:
                try:
                    links = self.page.locator(selector).all()
                    if links:
                        for link in links:
                            href = link.get_attribute('href')
                            if href and ('/p/' in href or '/reel/' in href):
                                full_url = f"https://www.instagram.com{href}" if href.startswith('/') else href
                                if full_url not in post_links:
                                    post_links.append(full_url)
                        break
                except:
                    continue
            
            print(f"   📊 Found {len(post_links)} post links")
            
            # Extract details from each post (limit to first 50)
            for i, post_url in enumerate(post_links[:50], 1):
                try:
                    if i % 10 == 0:
                        print(f"      Processing post {i}/{min(len(post_links), 50)}...")
                    
                    post_data = self._extract_post_details(post_url)
                    if post_data:
                        posts.append(post_data)
                    
                    time.sleep(1)  # Rate limiting
                
                except Exception as e:
                    print(f"      ⚠️  Error on post {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Error extracting posts: {e}")
        
        return posts
    
    def _extract_post_details(self, post_url: str) -> Optional[Dict]:
        """Extract details from a single post"""
        try:
            self.page.goto(post_url, timeout=15000)
            time.sleep(2)
            
            post_data = {
                'url': post_url,
                'type': None,
                'caption': None,
                'timestamp': None,
                'likes': None,
                'comments': None,
                'hashtags': [],
                'mentions': []
            }
            
            # Extract caption
            try:
                caption_selectors = [
                    'h1',
                    'div[class*="Caption"]',
                    'span[dir="auto"]'
                ]
                
                for selector in caption_selectors:
                    try:
                        caption = self.page.locator(selector).first.inner_text(timeout=3000)
                        if caption and len(caption) > 10:
                            post_data['caption'] = caption
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract hashtags from caption
            if post_data['caption']:
                hashtags = re.findall(r'#(\w+)', post_data['caption'])
                post_data['hashtags'] = hashtags
                
                mentions = re.findall(r'@(\w+)', post_data['caption'])
                post_data['mentions'] = mentions
            
            # Extract likes count
            try:
                like_selectors = [
                    'a[href*="/liked_by/"]',
                    'span:has-text("likes")',
                    'button:has-text("likes")'
                ]
                
                for selector in like_selectors:
                    try:
                        likes_elem = self.page.locator(selector).first
                        likes_text = likes_elem.inner_text(timeout=2000)
                        
                        # Extract number from text like "1,234 likes"
                        likes_match = re.search(r'([\d,]+)', likes_text)
                        if likes_match:
                            post_data['likes'] = likes_match.group(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract comments count
            try:
                comment_selectors = [
                    'a[href*="/comments/"]',
                    'span:has-text("comment")'
                ]
                
                for selector in comment_selectors:
                    try:
                        comments_elem = self.page.locator(selector).first
                        comments_text = comments_elem.inner_text(timeout=2000)
                        
                        comments_match = re.search(r'([\d,]+)', comments_text)
                        if comments_match:
                            post_data['comments'] = comments_match.group(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Determine post type
            if '/reel/' in post_url:
                post_data['type'] = 'reel'
            elif '/p/' in post_url:
                post_data['type'] = 'post'
            
            return post_data
        
        except Exception as e:
            return None
    
    def _analyze_hashtags(self, posts: List[Dict]) -> Dict:
        """Analyze hashtag usage"""
        all_hashtags = []
        
        for post in posts:
            if post.get('hashtags'):
                all_hashtags.extend(post['hashtags'])
        
        if not all_hashtags:
            return {'total_hashtags': 0, 'unique_hashtags': 0, 'top_hashtags': {}}
        
        hashtag_counts = Counter(all_hashtags)
        
        return {
            'total_hashtags': len(all_hashtags),
            'unique_hashtags': len(set(all_hashtags)),
            'top_hashtags': dict(hashtag_counts.most_common(10)),
            'avg_per_post': round(len(all_hashtags) / len(posts), 1) if posts else 0
        }
    
    def _analyze_engagement(self, posts: List[Dict]) -> Dict:
        """Analyze engagement metrics"""
        total_likes = 0
        total_comments = 0
        posts_with_likes = 0
        
        for post in posts:
            if post.get('likes'):
                try:
                    likes = int(post['likes'].replace(',', ''))
                    total_likes += likes
                    posts_with_likes += 1
                except:
                    pass
            
            if post.get('comments'):
                try:
                    comments = int(post['comments'].replace(',', ''))
                    total_comments += comments
                except:
                    pass
        
        return {
            'total_posts_analyzed': len(posts),
            'posts_with_data': posts_with_likes,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_likes': total_likes // posts_with_likes if posts_with_likes > 0 else 0,
            'avg_comments': total_comments // len(posts) if posts else 0
        }
    
    def _analyze_posting_patterns(self, posts: List[Dict]) -> Dict:
        """Analyze posting patterns"""
        patterns = {
            'total_posts': len(posts),
            'posts_with_hashtags': 0,
            'posts_with_mentions': 0,
            'reels_count': 0,
            'regular_posts_count': 0
        }
        
        for post in posts:
            if post.get('hashtags'):
                patterns['posts_with_hashtags'] += 1
            
            if post.get('mentions'):
                patterns['posts_with_mentions'] += 1
            
            if post.get('type') == 'reel':
                patterns['reels_count'] += 1
            elif post.get('type') == 'post':
                patterns['regular_posts_count'] += 1
        
        return patterns
    
    def _get_top_posts(self, posts: List[Dict]) -> List[Dict]:
        """Get top performing posts"""
        posts_with_likes = []
        
        for post in posts:
            if post.get('likes'):
                try:
                    likes = int(post['likes'].replace(',', ''))
                    posts_with_likes.append({
                        'url': post['url'],
                        'likes': likes,
                        'caption': post.get('caption', '')[:100] + '...' if post.get('caption') else None,
                        'hashtags': post.get('hashtags', [])
                    })
                except:
                    pass
        
        # Sort by likes
        posts_with_likes.sort(key=lambda x: x['likes'], reverse=True)
        
        return posts_with_likes[:5]
    
    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def save_data(self, data: Dict, username: str):
        """Save scraped data"""
        filename = f"{username}_instagram.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        import os
        size = os.path.getsize(filename) / 1024
        print(f"\n💾 Data saved: {filename} ({size:.1f} KB)")
        
        # Save posts separately
        if data.get('posts'):
            posts_file = f"{username}_instagram_posts.json"
            with open(posts_file, 'w') as f:
                json.dump(data['posts'], f, indent=2)
            print(f"💾 Posts saved: {posts_file}")
    
    def print_summary(self, data: Dict):
        """Print summary of scraped data"""
        print(f"\n{'='*70}")
        print("📊 INSTAGRAM SCRAPING SUMMARY")
        print("="*70)
        
        print(f"\n👤 Profile: @{data['username']}")
        
        if data.get('profile_info'):
            info = data['profile_info']
            print(f"\n📝 Profile Info:")
            print(f"   Full Name: {info.get('full_name', 'N/A')}")
            print(f"   Bio: {info.get('biography', 'N/A')[:60]}..." if info.get('biography') else "   Bio: N/A")
            print(f"   Verified: {'✓' if info.get('is_verified') else '✗'}")
            print(f"   Business: {'Yes' if info.get('is_business_account') else 'No'}")
            if info.get('external_url'):
                print(f"   Website: {info['external_url']}")
        
        if data.get('statistics'):
            stats = data['statistics']
            print(f"\n📈 Statistics:")
            print(f"   Posts: {stats.get('posts', 'N/A')}")
            print(f"   Followers: {stats.get('followers', 'N/A')}")
            print(f"   Following: {stats.get('following', 'N/A')}")
        
        if data.get('private_account'):
            print(f"\n🔒 Account is PRIVATE - posts not accessible")
        else:
            print(f"\n🎬 Content Scraped:")
            print(f"   Posts: {len(data.get('posts', []))}")
            
            if data.get('engagement_metrics'):
                eng = data['engagement_metrics']
                print(f"\n💡 Engagement:")
                print(f"   Total Likes: {eng.get('total_likes', 0):,}")
                print(f"   Total Comments: {eng.get('total_comments', 0):,}")
                print(f"   Avg Likes/Post: {eng.get('avg_likes', 0):,}")
                print(f"   Avg Comments/Post: {eng.get('avg_comments', 0):,}")
            
            if data.get('hashtag_analysis', {}).get('top_hashtags'):
                print(f"\n🏷️  Top Hashtags:")
                for tag, count in list(data['hashtag_analysis']['top_hashtags'].items())[:5]:
                    print(f"   #{tag}: {count} times")
            
            if data.get('top_posts'):
                print(f"\n🏆 Top Posts by Likes:")
                for i, post in enumerate(data['top_posts'][:3], 1):
                    print(f"   {i}. {post['likes']:,} likes")
                    if post.get('caption'):
                        print(f"      {post['caption']}")
                    print(f"      {post['url']}")
        
        print(f"\n⚠️  Note: Liked posts are private and cannot be scraped")
        print("="*70)


def main():
    username = "abby.barger"
    
    print("📸 Instagram Profile Scraper")
    print("="*70)
    print("⚠️  Note: Instagram liked posts are PRIVATE and cannot be scraped")
    print("="*70)
    
    scraper = InstagramScraper(headless=False)
    
    try:
        scraper.start()
        
        # Scrape profile
        data = scraper.scrape_profile(username)
        
        # Print summary
        scraper.print_summary(data)
        
        # Save data
        scraper.save_data(data, username)
        
        print(f"\n✅ INSTAGRAM SCRAPE COMPLETE!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

