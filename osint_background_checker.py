#!/usr/bin/env python3
"""
OSINT Background Investigation Framework
Inspired by: https://github.com/osintambition/Social-Media-OSINT-Tools-Collection

⚠️  FOR AUTHORIZED LEGAL USE ONLY
- Background checks (with consent)
- Investigative journalism
- Security research
- Law enforcement (with warrant)
- Due diligence

DO NOT use for:
- Stalking or harassment
- Identity theft
- Unauthorized surveillance
- Privacy violations
- Illegal purposes
"""

import json
import time
import re
from playwright.sync_api import sync_playwright
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import traceback


class OSINTBackgroundChecker:
    """
    Comprehensive OSINT Background Investigation Tool
    Searches across multiple platforms and data sources
    """
    
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        self.context = None
        
        # Investigation data
        self.investigation = {
            'subject': {},
            'platforms_found': [],
            'social_media_profiles': {},
            'public_records': {},
            'digital_footprint': {},
            'relationships': set(),
            'locations': [],
            'employment': [],
            'education': [],
            'contact_info': {
                'emails': set(),
                'phones': set(),
                'websites': set()
            },
            'timeline': [],
            'warnings': []
        }
    
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
        
        print("✅ OSINT framework initialized")
    
    def investigate(self, 
                   full_name: str = None,
                   username: str = None,
                   birthday: str = None,
                   phone: str = None,
                   hometown: str = None,
                   email: str = None) -> Dict:
        """
        Perform comprehensive background investigation
        
        Args:
            full_name: Person's full name
            username: Known username/handle
            birthday: Date of birth (YYYY-MM-DD or MM/DD/YYYY)
            phone: Phone number
            hometown: City/State
            email: Email address
        
        Returns:
            Complete investigation report
        """
        print(f"\n{'='*80}")
        print(f"🔍 OSINT BACKGROUND INVESTIGATION")
        print(f"{'='*80}\n")
        
        # Store subject information
        self.investigation['subject'] = {
            'full_name': full_name,
            'username': username,
            'birthday': birthday,
            'phone': phone,
            'hometown': hometown,
            'email': email,
            'investigation_date': datetime.now().isoformat()
        }
        
        report = {
            'subject_info': self.investigation['subject'],
            'investigation_summary': {},
            'social_media': {},
            'search_results': {},
            'people_search': {},
            'public_records': {},
            'cross_references': {},
            'timeline_reconstruction': [],
            'risk_indicators': {},
            'confidence_scores': {}
        }
        
        try:
            # Step 1: Social media username search
            if username:
                print(f"📱 Step 1: Social Media Username Search (@{username})")
                print(f"{'─'*80}")
                report['social_media'] = self._search_social_media_platforms(username)
            
            # Step 2: Full name search
            if full_name:
                print(f"\n👤 Step 2: Full Name Search ({full_name})")
                print(f"{'─'*80}")
                report['search_results']['name'] = self._search_by_name(full_name, hometown)
            
            # Step 3: Phone number search
            if phone:
                print(f"\n📞 Step 3: Phone Number Search")
                print(f"{'─'*80}")
                report['search_results']['phone'] = self._search_by_phone(phone)
            
            # Step 4: Email search
            if email:
                print(f"\n📧 Step 4: Email Address Search")
                print(f"{'─'*80}")
                report['search_results']['email'] = self._search_by_email(email)
            
            # Step 5: Location-based search
            if hometown and full_name:
                print(f"\n📍 Step 5: Location-Based Search ({hometown})")
                print(f"{'─'*80}")
                report['search_results']['location'] = self._search_by_location(full_name, hometown)
            
            # Step 6: People search engines
            if full_name:
                print(f"\n🔎 Step 6: People Search Engines")
                print(f"{'─'*80}")
                report['people_search'] = self._search_people_databases(full_name, hometown, birthday)
            
            # Step 7: Cross-reference and analyze
            print(f"\n🔬 Step 7: Cross-Reference Analysis")
            print(f"{'─'*80}")
            report['cross_references'] = self._cross_reference_data()
            report['timeline_reconstruction'] = self._reconstruct_timeline()
            report['confidence_scores'] = self._calculate_confidence_scores(report)
            
            # Step 8: Generate investigation summary
            print(f"\n📊 Step 8: Generating Investigation Summary")
            print(f"{'─'*80}")
            report['investigation_summary'] = self._generate_summary(report)
            
        except Exception as e:
            print(f"\n❌ Investigation error: {e}")
            traceback.print_exc()
            report['error'] = str(e)
        
        return report
    
    def _search_social_media_platforms(self, username: str) -> Dict:
        """Search for username across major social media platforms"""
        platforms = {
            'tiktok': f'https://www.tiktok.com/@{username}',
            'instagram': f'https://www.instagram.com/{username}/',
            'twitter': f'https://twitter.com/{username}',
            'facebook': f'https://www.facebook.com/{username}',
            'linkedin': f'https://www.linkedin.com/in/{username}',
            'reddit': f'https://www.reddit.com/user/{username}',
            'github': f'https://github.com/{username}',
            'youtube': f'https://www.youtube.com/@{username}',
            'pinterest': f'https://www.pinterest.com/{username}',
            'snapchat': f'https://www.snapchat.com/add/{username}'
        }
        
        results = {}
        
        for platform, url in platforms.items():
            try:
                print(f"   🔍 Checking {platform.capitalize()}...", end='')
                
                self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
                
                # Check if profile exists
                page_content = self.page.content().lower()
                
                # Detection patterns for each platform
                not_found_patterns = {
                    'tiktok': ['couldn\'t find this account', 'page not found'],
                    'instagram': ['sorry, this page', 'page not available'],
                    'twitter': ['this account doesn\'t exist', 'account suspended'],
                    'facebook': ['content not found', 'page not found'],
                    'linkedin': ['page not found', '404'],
                    'reddit': ['nobody on reddit goes by that name', 'page not found'],
                    'github': ['page not found', '404'],
                    'youtube': ['this page isn\'t available', 'not found'],
                    'pinterest': ['page not found', 'this user hasn\'t'],
                    'snapchat': ['page not found', 'not available']
                }
                
                not_found = any(pattern in page_content for pattern in not_found_patterns.get(platform, []))
                
                if not not_found:
                    # Profile likely exists
                    print(f" ✅ FOUND")
                    
                    results[platform] = {
                        'found': True,
                        'url': url,
                        'profile_data': self._extract_platform_data(platform, username)
                    }
                    
                    self.investigation['platforms_found'].append(platform)
                else:
                    print(f" ✗ Not found")
                    results[platform] = {'found': False, 'url': url}
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f" ⚠️  Error")
                results[platform] = {'found': False, 'error': str(e)}
        
        return results
    
    def _extract_platform_data(self, platform: str, username: str) -> Dict:
        """Extract available data from platform"""
        data = {'platform': platform, 'username': username}
        
        try:
            if platform == 'tiktok':
                # Use our proven TikTok extraction
                page_content = self.page.content()
                json_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', 
                                     page_content, re.DOTALL)
                
                if json_match:
                    universal_data = json.loads(json_match.group(1))
                    user_detail = universal_data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
                    user_info = user_detail.get('userInfo', {})
                    user = user_info.get('user', {})
                    stats = user_info.get('stats', {})
                    
                    data.update({
                        'display_name': user.get('nickname'),
                        'bio': user.get('signature'),
                        'followers': stats.get('followerCount', 0),
                        'following': stats.get('followingCount', 0),
                        'verified': user.get('verified', False)
                    })
            
            elif platform == 'instagram':
                meta_desc = self.page.locator('meta[property="og:description"]').get_attribute('content', timeout=3000)
                
                if meta_desc:
                    followers_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta_desc)
                    posts_match = re.search(r'([\d,\.]+[KMB]?)\s+Posts', meta_desc)
                    
                    data.update({
                        'followers': followers_match.group(1) if followers_match else None,
                        'posts': posts_match.group(1) if posts_match else None
                    })
            
            elif platform == 'linkedin':
                # Extract name and headline if visible
                try:
                    title = self.page.title()
                    if title:
                        data['page_title'] = title
                except:
                    pass
        
        except Exception as e:
            data['extraction_error'] = str(e)
        
        return data
    
    def _search_by_name(self, full_name: str, hometown: str = None) -> Dict:
        """Search by full name across search engines and people databases"""
        results = {
            'google_results': [],
            'people_search_engines': {},
            'social_mentions': []
        }
        
        # Google search with quotes for exact name
        search_queries = [
            f'"{full_name}"',
            f'"{full_name}" {hometown}' if hometown else None,
            f'"{full_name}" instagram',
            f'"{full_name}" tiktok',
            f'"{full_name}" linkedin',
            f'"{full_name}" facebook'
        ]
        
        search_queries = [q for q in search_queries if q]
        
        print(f"   🔍 Running {len(search_queries)} Google searches...")
        
        for query in search_queries[:3]:  # Limit to avoid rate limiting
            try:
                google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                self.page.goto(google_url, timeout=15000)
                time.sleep(2)
                
                # Extract search result titles and URLs
                result_links = self.page.locator('a h3').all()
                
                for link in result_links[:5]:
                    try:
                        title = link.inner_text(timeout=1000)
                        parent = link.locator('..')
                        href = parent.get_attribute('href', timeout=1000)
                        
                        if title and href:
                            results['google_results'].append({
                                'title': title,
                                'url': href,
                                'query': query
                            })
                    except:
                        continue
                
                time.sleep(2)
            
            except Exception as e:
                print(f"      ⚠️  Google search error: {e}")
        
        print(f"      ✓ Found {len(results['google_results'])} Google results")
        
        # People search engines (public databases)
        people_search_sites = {
            'whitepages': f'https://www.whitepages.com/name/{full_name.replace(" ", "-")}',
            'spokeo': f'https://www.spokeo.com/{full_name.replace(" ", "-")}',
            'pipl': f'https://pipl.com/search/?q={full_name.replace(" ", "+")}',
            'truepeoplesearch': f'https://www.truepeoplesearch.com/results?name={full_name.replace(" ", "%20")}'
        }
        
        print(f"   🔍 Checking people search databases...")
        
        for site, url in people_search_sites.items():
            try:
                print(f"      Checking {site}...", end='')
                
                self.page.goto(url, timeout=15000)
                time.sleep(3)
                
                # Check if results found
                page_text = self.page.content().lower()
                
                has_results = not any(phrase in page_text for phrase in [
                    'no results', 'not found', '0 results', 'no records'
                ])
                
                results['people_search_engines'][site] = {
                    'checked': True,
                    'url': url,
                    'potential_results': has_results
                }
                
                print(f" {'✅' if has_results else '✗'}")
                
                time.sleep(2)
            
            except Exception as e:
                print(f" ⚠️")
                results['people_search_engines'][site] = {'checked': False, 'error': str(e)}
        
        return results
    
    def _search_by_phone(self, phone: str) -> Dict:
        """Search by phone number"""
        results = {
            'reverse_lookup': {},
            'social_media': {},
            'carrier_info': {}
        }
        
        # Clean phone number
        phone_clean = re.sub(r'[^\d]', '', phone)
        
        print(f"   📞 Searching phone: {phone}")
        
        # Reverse phone lookup sites
        lookup_sites = {
            'truecaller_web': f'https://www.truecaller.com/search/us/{phone_clean}',
            'whitepages': f'https://www.whitepages.com/phone/{phone_clean}',
            'spy_dialer': f'https://www.spydialer.com/default.aspx?phone={phone_clean}'
        }
        
        for site, url in lookup_sites.items():
            try:
                print(f"      Checking {site}...", end='')
                
                self.page.goto(url, timeout=15000)
                time.sleep(3)
                
                page_text = self.page.content()
                
                results['reverse_lookup'][site] = {
                    'checked': True,
                    'url': url,
                    'page_loaded': True
                }
                
                print(f" ✓")
                time.sleep(2)
            
            except Exception as e:
                print(f" ⚠️")
                results['reverse_lookup'][site] = {'checked': False, 'error': str(e)}
        
        # Check if phone is associated with social media
        # Facebook recover lookup
        try:
            print(f"      Checking Facebook phone recovery...", end='')
            self.page.goto('https://www.facebook.com/login/identify/?ctx=recover', timeout=15000)
            time.sleep(2)
            
            # Enter phone number
            self.page.fill('input[name="email"]', phone, timeout=5000)
            self.page.click('button[type="submit"]', timeout=5000)
            time.sleep(3)
            
            page_text = self.page.content().lower()
            
            # Check if account found
            fb_found = 'no search results' not in page_text and 'we couldn\'t find' not in page_text
            
            results['social_media']['facebook'] = {
                'phone_associated': fb_found
            }
            
            print(f" {'✅' if fb_found else '✗'}")
        
        except Exception as e:
            print(f" ⚠️")
            results['social_media']['facebook'] = {'error': str(e)}
        
        return results
    
    def _search_by_email(self, email: str) -> Dict:
        """Search by email address"""
        results = {
            'breach_check': {},
            'social_media': {},
            'professional': {}
        }
        
        print(f"   📧 Searching email: {email}")
        
        # Check if email is associated with social accounts
        # Facebook email lookup
        try:
            print(f"      Checking Facebook email recovery...", end='')
            self.page.goto('https://www.facebook.com/login/identify/?ctx=recover', timeout=15000)
            time.sleep(2)
            
            self.page.fill('input[name="email"]', email, timeout=5000)
            self.page.click('button[type="submit"]', timeout=5000)
            time.sleep(3)
            
            page_text = self.page.content().lower()
            fb_found = 'no search results' not in page_text and 'we couldn\'t find' not in page_text
            
            results['social_media']['facebook'] = {
                'email_associated': fb_found
            }
            
            print(f" {'✅' if fb_found else '✗'}")
        
        except Exception as e:
            print(f" ⚠️")
            results['social_media']['facebook'] = {'error': str(e)}
        
        # Google the email
        try:
            print(f"      Google search for email...", end='')
            google_url = f'https://www.google.com/search?q="{email}"'
            self.page.goto(google_url, timeout=15000)
            time.sleep(2)
            
            # Count results
            result_count = self.page.locator('a h3').count()
            
            results['google_search'] = {
                'results_found': result_count,
                'url': google_url
            }
            
            print(f" {result_count} results")
        
        except Exception as e:
            print(f" ⚠️")
        
        return results
    
    def _search_by_location(self, name: str, location: str) -> Dict:
        """Search by name and location"""
        results = {
            'local_searches': [],
            'address_databases': {}
        }
        
        search_query = f'"{name}" "{location}"'
        print(f"   📍 Searching: {search_query}")
        
        try:
            # Google search with location
            google_url = f'https://www.google.com/search?q={search_query.replace(" ", "+")}'
            self.page.goto(google_url, timeout=15000)
            time.sleep(2)
            
            # Extract results
            result_links = self.page.locator('a h3').all()
            
            for link in result_links[:10]:
                try:
                    title = link.inner_text(timeout=1000)
                    parent = link.locator('..')
                    href = parent.get_attribute('href', timeout=1000)
                    
                    if title and href:
                        results['local_searches'].append({
                            'title': title,
                            'url': href
                        })
                except:
                    continue
            
            print(f"      ✓ Found {len(results['local_searches'])} location-based results")
        
        except Exception as e:
            print(f"      ⚠️  Error: {e}")
        
        return results
    
    def _search_people_databases(self, name: str, location: str = None, birthday: str = None) -> Dict:
        """Search people search engines and public databases"""
        results = {
            'whitepages': {},
            'truepeoplesearch': {},
            'fastpeoplesearch': {},
            'fastbackgroundcheck': {}
        }
        
        # Whitepages search
        try:
            print(f"      Checking Whitepages...", end='')
            
            query = name.replace(' ', '-')
            if location:
                query += f'-{location.replace(" ", "-")}'
            
            wp_url = f'https://www.whitepages.com/name/{query}'
            self.page.goto(wp_url, timeout=15000)
            time.sleep(3)
            
            page_text = self.page.content()
            
            results['whitepages'] = {
                'checked': True,
                'url': wp_url,
                'results_visible': 'results' in page_text.lower()
            }
            
            print(f" ✓")
        
        except Exception as e:
            print(f" ⚠️")
            results['whitepages'] = {'error': str(e)}
        
        # TruePeopleSearch
        try:
            print(f"      Checking TruePeopleSearch...", end='')
            
            tps_url = f'https://www.truepeoplesearch.com/results?name={name.replace(" ", "%20")}'
            if location:
                tps_url += f'&citystatezip={location.replace(" ", "%20")}'
            
            self.page.goto(tps_url, timeout=15000)
            time.sleep(3)
            
            results['truepeoplesearch'] = {
                'checked': True,
                'url': tps_url
            }
            
            print(f" ✓")
        
        except Exception as e:
            print(f" ⚠️")
            results['truepeoplesearch'] = {'error': str(e)}
        
        return results
    
    def _cross_reference_data(self) -> Dict:
        """Cross-reference data from multiple sources"""
        cross_ref = {
            'platform_overlap': len(self.investigation['platforms_found']),
            'common_usernames': self.investigation['platforms_found'],
            'verified_accounts': [],
            'confidence_level': 'UNKNOWN'
        }
        
        # Calculate confidence
        if cross_ref['platform_overlap'] >= 3:
            cross_ref['confidence_level'] = 'HIGH'
        elif cross_ref['platform_overlap'] >= 2:
            cross_ref['confidence_level'] = 'MEDIUM'
        elif cross_ref['platform_overlap'] >= 1:
            cross_ref['confidence_level'] = 'LOW'
        
        print(f"      ✓ Cross-referenced {cross_ref['platform_overlap']} platforms")
        print(f"      ✓ Confidence level: {cross_ref['confidence_level']}")
        
        return cross_ref
    
    def _reconstruct_timeline(self) -> List[Dict]:
        """Reconstruct timeline of digital activity"""
        timeline = []
        
        # This would need post dates from scraped content
        # For now, just create framework
        
        return timeline
    
    def _calculate_confidence_scores(self, report: Dict) -> Dict:
        """Calculate confidence scores for findings"""
        scores = {
            'username_match': 0,
            'name_match': 0,
            'location_match': 0,
            'overall_confidence': 0
        }
        
        # Calculate based on matches found
        social_media = report.get('social_media', {})
        found_count = sum(1 for platform, data in social_media.items() 
                         if data.get('found'))
        
        if found_count >= 3:
            scores['username_match'] = 90
        elif found_count >= 2:
            scores['username_match'] = 70
        elif found_count == 1:
            scores['username_match'] = 50
        
        # Overall confidence
        scores['overall_confidence'] = (
            scores['username_match'] + 
            scores['name_match'] + 
            scores['location_match']
        ) // 3
        
        return scores
    
    def _generate_summary(self, report: Dict) -> Dict:
        """Generate investigation summary"""
        summary = {
            'total_platforms_checked': 0,
            'profiles_found': 0,
            'data_points_collected': 0,
            'confidence_score': 0,
            'investigation_completeness': 0
        }
        
        # Count platforms
        if 'social_media' in report:
            summary['total_platforms_checked'] = len(report['social_media'])
            summary['profiles_found'] = sum(1 for p, d in report['social_media'].items() if d.get('found'))
        
        # Confidence
        if 'confidence_scores' in report:
            summary['confidence_score'] = report['confidence_scores'].get('overall_confidence', 0)
        
        # Completeness
        if summary['total_platforms_checked'] > 0:
            summary['investigation_completeness'] = int(
                (summary['profiles_found'] / summary['total_platforms_checked']) * 100
            )
        
        return summary
    
    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def save_investigation_report(self, report: Dict, identifier: str):
        """Save comprehensive investigation report"""
        filename = f"{identifier}_osint_background_report.json"
        
        # Convert sets to lists for JSON serialization
        report_copy = json.loads(json.dumps(report, default=str))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_copy, f, indent=2, ensure_ascii=False)
        
        import os
        size = os.path.getsize(filename) / 1024
        print(f"\n💾 Investigation report saved: {filename} ({size:.1f} KB)")
        
        # Also save as readable text report
        self._save_text_report(report, identifier)
    
    def _save_text_report(self, report: Dict, identifier: str):
        """Save human-readable text report"""
        filename = f"{identifier}_osint_report.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("OSINT BACKGROUND INVESTIGATION REPORT\n")
            f.write("="*80 + "\n\n")
            
            # Subject information
            subject = report.get('subject_info', {})
            f.write("SUBJECT INFORMATION:\n")
            f.write("-"*80 + "\n")
            for key, value in subject.items():
                if value:
                    f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
            
            # Summary
            summary = report.get('investigation_summary', {})
            f.write("\n" + "="*80 + "\n")
            f.write("INVESTIGATION SUMMARY:\n")
            f.write("-"*80 + "\n")
            f.write(f"  Platforms Checked: {summary.get('total_platforms_checked', 0)}\n")
            f.write(f"  Profiles Found: {summary.get('profiles_found', 0)}\n")
            f.write(f"  Confidence Score: {summary.get('confidence_score', 0)}%\n")
            f.write(f"  Completeness: {summary.get('investigation_completeness', 0)}%\n")
            
            # Social media findings
            f.write("\n" + "="*80 + "\n")
            f.write("SOCIAL MEDIA PROFILES FOUND:\n")
            f.write("-"*80 + "\n")
            
            social_media = report.get('social_media', {})
            for platform, data in social_media.items():
                if data.get('found'):
                    f.write(f"\n  ✓ {platform.upper()}\n")
                    f.write(f"    URL: {data.get('url', 'N/A')}\n")
                    
                    if data.get('profile_data'):
                        profile = data['profile_data']
                        for key, value in profile.items():
                            if key not in ['platform', 'username', 'extraction_error']:
                                f.write(f"    {key.replace('_', ' ').title()}: {value}\n")
            
            # Cross-references
            cross_ref = report.get('cross_references', {})
            f.write("\n" + "="*80 + "\n")
            f.write("CROSS-REFERENCE ANALYSIS:\n")
            f.write("-"*80 + "\n")
            f.write(f"  Platforms with Same Username: {cross_ref.get('platform_overlap', 0)}\n")
            f.write(f"  Confidence Level: {cross_ref.get('confidence_level', 'UNKNOWN')}\n")
            
            # Disclaimer
            f.write("\n" + "="*80 + "\n")
            f.write("DISCLAIMER:\n")
            f.write("-"*80 + "\n")
            f.write("This report contains publicly available information only.\n")
            f.write("All data should be verified independently.\n")
            f.write("Use only for authorized, legal purposes.\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"💾 Text report saved: {filename}")
    
    def print_comprehensive_report(self, report: Dict):
        """Print comprehensive investigation report"""
        print(f"\n{'='*80}")
        print(f"📊 OSINT BACKGROUND INVESTIGATION REPORT")
        print(f"{'='*80}\n")
        
        # Subject
        subject = report.get('subject_info', {})
        print(f"🎯 SUBJECT:")
        for key, value in subject.items():
            if value and key != 'investigation_date':
                print(f"   {key.replace('_', ' ').title()}: {value}")
        
        # Summary
        summary = report.get('investigation_summary', {})
        print(f"\n📈 INVESTIGATION SUMMARY:")
        print(f"   Platforms Checked: {summary.get('total_platforms_checked', 0)}")
        print(f"   Profiles Found: {summary.get('profiles_found', 0)}")
        print(f"   Confidence Score: {summary.get('confidence_score', 0)}%")
        print(f"   Completeness: {summary.get('investigation_completeness', 0)}%")
        
        # Platforms found
        print(f"\n📱 SOCIAL MEDIA PROFILES:")
        social_media = report.get('social_media', {})
        
        found_platforms = [p for p, d in social_media.items() if d.get('found')]
        not_found = [p for p, d in social_media.items() if not d.get('found')]
        
        for platform in found_platforms:
            data = social_media[platform]
            print(f"   ✅ {platform.upper()}")
            print(f"      URL: {data.get('url', 'N/A')}")
            
            if data.get('profile_data'):
                profile = data['profile_data']
                if profile.get('followers'):
                    print(f"      Followers: {profile['followers']}")
                if profile.get('display_name'):
                    print(f"      Name: {profile['display_name']}")
        
        for platform in not_found:
            print(f"   ✗ {platform.capitalize()}: Not found")
        
        # Search results
        if report.get('search_results'):
            print(f"\n🔍 SEARCH RESULTS:")
            
            if 'name' in report['search_results']:
                name_results = report['search_results']['name']
                if name_results.get('google_results'):
                    print(f"   Google: {len(name_results['google_results'])} results")
                
                if name_results.get('people_search_engines'):
                    databases = name_results['people_search_engines']
                    found = [db for db, info in databases.items() if info.get('potential_results')]
                    if found:
                        print(f"   People Search: Found in {', '.join(found)}")
        
        # Cross-references
        cross_ref = report.get('cross_references', {})
        if cross_ref:
            print(f"\n🔬 CROSS-REFERENCE ANALYSIS:")
            print(f"   Platform Overlap: {cross_ref.get('platform_overlap', 0)}")
            print(f"   Confidence Level: {cross_ref.get('confidence_level', 'UNKNOWN')}")
        
        # Confidence scores
        confidence = report.get('confidence_scores', {})
        if confidence:
            print(f"\n📊 CONFIDENCE SCORES:")
            print(f"   Username Match: {confidence.get('username_match', 0)}%")
            print(f"   Overall Confidence: {confidence.get('overall_confidence', 0)}%")
        
        print(f"\n{'='*80}")
        print(f"⚠️  LEGAL NOTICE:")
        print(f"This tool is for authorized investigations only.")
        print(f"Always comply with privacy laws and obtain proper consent.")
        print(f"Inspired by: github.com/osintambition/Social-Media-OSINT-Tools-Collection")
        print(f"{'='*80}\n")


def main():
    """Main execution"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║         ADVANCED OSINT BACKGROUND INVESTIGATION FRAMEWORK                ║
║         Inspired by: github.com/osintambition                            ║
║                                                                           ║
║  ⚠️  AUTHORIZED USE ONLY - FOR LEGAL PURPOSES                            ║
║                                                                           ║
║  Use Cases:                                                              ║
║  ✓ Pre-employment screening (with consent)                              ║
║  ✓ Investigative journalism                                             ║
║  ✓ Security research                                                    ║
║  ✓ Due diligence                                                        ║
║  ✗ Stalking, harassment, or privacy violations                         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Example investigation
    # Change these values for your investigation
    investigation_params = {
        'full_name': 'Abigail Lauren Barger',    # Full name
        'username': 'abby.barger',                # Instagram username
        'birthday': '2004-04-04',                 # Birthday (YYYY-MM-DD)
        'phone': '636-432-8287',                  # Phone number
        'hometown': 'Ballwin, Missouri',          # City, State
        'email': 'abarger04@gmail.com'            # Email address
    }
    
    print(f"🔍 Investigation Parameters:")
    for key, value in investigation_params.items():
        if value:
            print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    confirm = input("\n⚠️  Proceed with investigation? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Investigation cancelled")
        return
    
    scraper = OSINTBackgroundChecker(headless=False)
    
    try:
        scraper.start()
        
        # Run comprehensive investigation
        report = scraper.investigate(**investigation_params)
        
        # Print report
        scraper.print_comprehensive_report(report)
        
        # Save report
        identifier = investigation_params.get('username') or investigation_params.get('full_name', 'subject').replace(' ', '_')
        scraper.save_investigation_report(report, identifier)
        
        print(f"\n✅ INVESTIGATION COMPLETE!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

