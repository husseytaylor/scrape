# Snapchat Activity Scraper Configuration Guide

## ⚠️ Critical Differences: TikTok vs Snapchat

### TikTok (What We Built)
✅ Public profiles accessible without login  
✅ Content visible in browser  
✅ API responses can be intercepted  
✅ No authentication required for public data  

### Snapchat (What You're Asking For)
❌ **No public profiles** - Everything requires authentication  
❌ **Ephemeral content** - Stories disappear after 24 hours  
❌ **Heavy anti-scraping measures** - Sophisticated bot detection  
❌ **Must be logged in** - Cannot view anything without account  
❌ **Mobile-first** - Limited web interface  
❌ **Encrypted API** - Many endpoints use encryption  

---

## 🚨 Major Challenges

### 1. **Authentication Required**
Unlike TikTok, Snapchat requires you to be logged in to see ANY content:
- Need valid Snapchat credentials
- Two-factor authentication handling
- Session management
- Cookie/token handling

### 2. **Anti-Bot Detection**
Snapchat has aggressive anti-scraping measures:
- Device fingerprinting
- Behavioral analysis
- CAPTCHA challenges
- IP rate limiting
- Account flagging/banning

### 3. **Limited Web Interface**
Snapchat is primarily mobile-first:
- Most features only on mobile app
- Web interface (`web.snapchat.com`) has limited functionality
- May need mobile app API reverse engineering

### 4. **Legal & Ethical Issues**
⚠️ **MORE RESTRICTIVE THAN TIKTOK:**
- Violates Snapchat Terms of Service
- Privacy concerns (personal communications)
- Potential legal consequences
- Account termination risk

---

## 🛠️ Required Configuration Changes

### 1. Authentication System

```python
class SnapchatScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth_token = None
        self.session = None
    
    def login(self):
        """Handle Snapchat login"""
        # Navigate to login page
        self.page.goto("https://accounts.snapchat.com/accounts/login")
        
        # Fill credentials
        self.page.fill('input[name="username"]', self.username)
        self.page.fill('input[name="password"]', self.password)
        self.page.click('button[type="submit"]')
        
        # Handle 2FA if required
        if self.page.locator('input[name="code"]').count() > 0:
            code = input("Enter 2FA code: ")
            self.page.fill('input[name="code"]', code)
            self.page.click('button[type="submit"]')
        
        # Wait for successful login
        self.page.wait_for_url("**/web/**", timeout=30000)
        
        # Save cookies/tokens
        self.save_session()
```

### 2. Mobile User Agent (Critical)

Snapchat's web interface is limited. You may need to emulate mobile:

```python
def start(self):
    """Initialize with mobile emulation"""
    # Use mobile device emulation
    iphone_13 = self.playwright.devices['iPhone 13 Pro']
    
    self.context = self.browser.new_context(
        **iphone_13,
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
        locale='en-US',
        timezone_id='America/New_York',
        geolocation={'latitude': 40.7128, 'longitude': -74.0060},
        permissions=['geolocation']
    )
```

### 3. Session Persistence

Save and reuse sessions to avoid repeated logins:

```python
def save_session(self):
    """Save authentication session"""
    cookies = self.context.cookies()
    with open('snapchat_session.json', 'w') as f:
        json.dump(cookies, f)

def load_session(self):
    """Load existing session"""
    try:
        with open('snapchat_session.json', 'r') as f:
            cookies = json.load(f)
        self.context.add_cookies(cookies)
        return True
    except:
        return False
```

### 4. Rate Limiting & Delays

More aggressive rate limiting needed:

```python
import random

def respectful_delay(self):
    """Random delays to mimic human behavior"""
    time.sleep(random.uniform(2, 5))

def scroll_slowly(self):
    """Slow, human-like scrolling"""
    for _ in range(10):
        self.page.mouse.wheel(0, random.randint(100, 300))
        time.sleep(random.uniform(0.5, 1.5))
```

---

## 📊 What Data Can Be Scraped?

### Accessible with Authentication:

#### Your Own Account
✅ Your stories (before they expire)  
✅ Your snap score  
✅ Your friend list  
✅ Your Bitmoji  
✅ Your memories (saved snaps)  
✅ Your chat history  

#### Friends' Content
✅ Friends' public stories  
✅ Friends' snap scores (if visible)  
✅ Friends' usernames  
✅ Story view counts (your own stories)  
⚠️ Chat messages (privacy violation)  
❌ Private snaps (impossible without account access)  

#### Discover Content
✅ Discover stories from publishers  
✅ Spotlight videos  
✅ Public stories  

---

## 🔧 Required Code Modifications

### Key Differences from TikTok Scraper:

```python
class SnapchatActivityScraper:
    def __init__(self, username, password, headless=False):
        self.username = username
        self.password = password
        self.headless = headless
        
    def scrape_profile(self, target_username):
        """
        Scrape Snapchat profile data
        NOTE: Must be friends with target to see most content
        """
        # Login first
        if not self.load_session():
            self.login()
        
        # Navigate to profile
        profile_url = f"https://web.snapchat.com/add/{target_username}"
        self.page.goto(profile_url)
        
        # Check if you're friends
        if not self.are_friends(target_username):
            print(f"❌ Not friends with {target_username}")
            print("⚠️  Most content will be unavailable")
        
        # Scrape available data...
```

### API Interception for Snapchat

```python
def _handle_response(self, response):
    """Intercept Snapchat API calls"""
    url = response.url
    
    # Snapchat API endpoints
    api_patterns = [
        'bitmoji.api.snapchat.com',
        'app.snapchat.com/web',
        'gql.snapchat.com',  # GraphQL endpoint
        'ms.sc-jpl.com'       # Media service
    ]
    
    if any(pattern in url for pattern in api_patterns):
        try:
            # May be encrypted/compressed
            data = response.json()
            self.captured_responses.append({
                'url': url,
                'data': data
            })
        except:
            # Handle binary/encrypted responses
            pass
```

---

## 🎯 Recommended Approach

### Option 1: Use Snapchat's Official API (BEST)
```python
"""
Snapchat offers a limited Public API for developers
- Login Kit for authentication
- Bitmoji Kit for avatars
- Creative Kit for sharing

Website: https://developers.snap.com/
"""
```

### Option 2: Scrape Your Own Account Only
```python
"""
Safest legal approach:
1. Login to your account
2. Scrape only YOUR data
3. Export YOUR memories/stories
4. Analyze YOUR activity

This avoids privacy violations
"""
```

### Option 3: Use Unofficial APIs (RISKY)
```python
"""
Some Python libraries attempt Snapchat scraping:
- snapchat-dl (story downloader)
- snap-scraper (deprecated)

⚠️  All violate ToS and may result in ban
"""
```

---

## 📝 Example Snapchat Scraper Structure

```python
#!/usr/bin/env python3
"""
Snapchat Activity Scraper
⚠️  For educational purposes only - violates Snapchat ToS
"""

from playwright.sync_api import sync_playwright
import json
import time
import random

class SnapchatScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.authenticated = False
    
    def start(self):
        self.playwright = sync_playwright().start()
        
        # Use mobile device
        iphone = self.playwright.devices['iPhone 13']
        
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            **iphone,
            locale='en-US'
        )
        self.page = self.context.new_page()
        
        # Intercept API calls
        self.page.on("response", self._handle_api_response)
    
    def login(self):
        """Login to Snapchat"""
        print("🔐 Logging in to Snapchat...")
        
        # Navigate to Snapchat web
        self.page.goto("https://accounts.snapchat.com/accounts/login")
        time.sleep(2)
        
        # Fill login form
        self.page.fill('input[name="username"]', self.username)
        time.sleep(random.uniform(0.5, 1))
        self.page.fill('input[name="password"]', self.password)
        time.sleep(random.uniform(0.5, 1))
        
        # Submit
        self.page.click('button[type="submit"]')
        
        # Wait and check
        try:
            self.page.wait_for_url("**/web/**", timeout=30000)
            self.authenticated = True
            print("✅ Login successful")
            
            # Save cookies
            self._save_cookies()
        except:
            print("❌ Login failed - may need 2FA")
            return False
        
        return True
    
    def scrape_my_data(self):
        """Scrape your own account data"""
        if not self.authenticated:
            print("❌ Must login first")
            return None
        
        data = {
            'username': self.username,
            'friends': self._get_friends(),
            'stories': self._get_my_stories(),
            'snap_score': self._get_snap_score(),
            'memories': self._get_memories()
        }
        
        return data
    
    def _get_friends(self):
        """Get friend list"""
        print("📱 Getting friend list...")
        friends = []
        
        try:
            self.page.goto("https://web.snapchat.com/friends")
            time.sleep(3)
            
            # Scroll to load all friends
            for _ in range(10):
                self.page.keyboard.press('End')
                time.sleep(1)
            
            # Extract friend elements
            friend_elements = self.page.locator('[data-testid="friend-item"]').all()
            
            for element in friend_elements:
                try:
                    username = element.locator('.username').inner_text()
                    display_name = element.locator('.display-name').inner_text()
                    friends.append({
                        'username': username,
                        'display_name': display_name
                    })
                except:
                    continue
        
        except Exception as e:
            print(f"⚠️  Error getting friends: {e}")
        
        return friends
    
    def _get_my_stories(self):
        """Get your stories"""
        print("📸 Getting your stories...")
        stories = []
        
        try:
            self.page.goto("https://web.snapchat.com/my-story")
            time.sleep(3)
            
            # Extract story data from API responses
            # This would be captured via response interception
            
        except Exception as e:
            print(f"⚠️  Error getting stories: {e}")
        
        return stories
    
    def _get_snap_score(self):
        """Get snap score"""
        try:
            self.page.goto("https://web.snapchat.com/settings")
            time.sleep(2)
            
            score = self.page.locator('[data-testid="snap-score"]').inner_text()
            return score
        except:
            return None
    
    def _get_memories(self):
        """Get saved memories"""
        print("💾 Getting memories...")
        memories = []
        
        try:
            self.page.goto("https://web.snapchat.com/memories")
            time.sleep(3)
            
            # Scroll and load memories
            # Extract memory data
            
        except Exception as e:
            print(f"⚠️  Error getting memories: {e}")
        
        return memories
    
    def _handle_api_response(self, response):
        """Capture API responses"""
        if 'snapchat.com' in response.url:
            try:
                if response.status == 200:
                    # Try to parse JSON
                    data = response.json()
                    # Process and store
            except:
                pass
    
    def _save_cookies(self):
        """Save authentication cookies"""
        cookies = self.context.cookies()
        with open('snapchat_cookies.json', 'w') as f:
            json.dump(cookies, f)
    
    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()


def main():
    # Your Snapchat credentials
    username = input("Snapchat username: ")
    password = input("Snapchat password: ")
    
    scraper = SnapchatScraper(username, password)
    
    try:
        scraper.start()
        
        if scraper.login():
            # Scrape YOUR data only
            my_data = scraper.scrape_my_data()
            
            # Save to file
            with open('my_snapchat_data.json', 'w') as f:
                json.dump(my_data, f, indent=2)
            
            print("\n✅ Data saved to my_snapchat_data.json")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    print("⚠️  WARNING: This violates Snapchat Terms of Service")
    print("⚠️  Use at your own risk - account may be banned")
    print("⚠️  Only scrape YOUR OWN data\n")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        main()
```

---

## ⚠️ Legal & Ethical Warnings

### Terms of Service Violations
Snapchat's ToS explicitly prohibit:
- Automated access without permission
- Scraping user data
- Reverse engineering APIs
- Creating unauthorized bots

### Potential Consequences
- **Account ban** (permanent)
- **IP blocking**
- **Legal action** (if scraping other users' data)
- **Privacy violations** (if accessing private content)
- **Criminal charges** (in some jurisdictions for unauthorized access)

### Safer Alternatives
1. **Request data from Snapchat directly:**
   - Settings → "My Data" → "Submit Request"
   - Legal way to get YOUR data

2. **Use official Snap Kit SDKs:**
   - Creative Kit, Login Kit, Bitmoji Kit
   - https://developers.snap.com/

3. **Manual export:**
   - Save your stories manually
   - Screenshot important content

---

## 🆚 TikTok vs Snapchat Scraping Comparison

| Feature | TikTok | Snapchat |
|---------|---------|-----------|
| **Public Access** | ✅ Yes | ❌ No |
| **Login Required** | ❌ No | ✅ Yes |
| **Web Interface** | ✅ Full | ⚠️ Limited |
| **API Access** | ✅ Interceptable | ⚠️ Encrypted |
| **Legal Risk** | 🟡 Medium | 🔴 High |
| **Ban Risk** | 🟡 Low-Medium | 🔴 Very High |
| **Difficulty** | 🟢 Easy | 🔴 Very Hard |
| **Success Rate** | 70-90% | 10-30% |

---

## 🎯 Recommendation

**For Snapchat, I recommend:**

1. **DON'T scrape other users' data** - High legal/ethical risk
2. **DO use Snapchat's Data Download feature** - Get your data legally
3. **DO use official Snap Kit if building apps** - Proper developer access
4. **DON'T violate privacy** - Snapchat is meant to be ephemeral

**If you MUST scrape:**
- Only your own account
- Use responsibly
- Expect account bans
- Don't save others' private content
- Consider legal implications

---

## 📚 Resources

- **Snapchat ToS:** https://www.snap.com/en-US/terms
- **Snap Kit Developers:** https://developers.snap.com/
- **Data Download:** Settings → My Data in Snapchat app
- **Privacy Policy:** https://www.snap.com/en-US/privacy/privacy-policy

---

**Bottom Line:** Snapchat scraping is **significantly harder** and **legally riskier** than TikTok. Unless you have a very specific use case and are willing to accept the risks, I recommend using official channels or manual methods instead.

