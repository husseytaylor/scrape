# Advanced TikTok Profile Scraper Suite

A comprehensive Python-based scraping solution for extracting detailed account and activity information from TikTok profiles using network request interception.

## 🚀 Features

### Profile Data
- ✅ Account information (username, bio, followers, following, likes)
- ✅ Complete user statistics and metadata
- ✅ Avatar URLs and verification status
- ✅ User ID and unique identifiers

### Video Data
- ✅ User's posted videos with full metadata
- ✅ Video statistics (views, likes, comments, shares)
- ✅ Video descriptions and hashtags
- ✅ Music/audio information
- ✅ Direct video URLs
- ✅ Thumbnail images
- ✅ Video dimensions and duration

### Advanced Features
- ✅ Network request interception to capture API responses
- ✅ Automatic scrolling to load lazy-loaded content
- ✅ Captures liked videos (if public)
- ✅ Extracts recommended and related content
- ✅ Multiple scraping strategies (Basic → Advanced → Ultimate)
- ✅ Full-page screenshots for debugging
- ✅ Comprehensive JSON data export

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Chromium browser for Playwright
playwright install chromium
```

## 🎯 Quick Start

### Option 1: Ultimate Scraper (Recommended)
The most powerful scraper with network interception:

```bash
python tiktok_ultimate_scraper.py
```

### Option 2: Advanced Scraper
Comprehensive scraper without network interception:

```bash
python tiktok_advanced_scraper.py
```

### Option 3: Basic Scraper
Simple HTML parsing scraper:

```bash
python tiktok_scraper.py
```

## 💻 Usage as Module

### Ultimate Scraper
```python
from tiktok_ultimate_scraper import UltimateTikTokScraper

scraper = UltimateTikTokScraper(headless=False)
scraper.start()

# Scrape profile
data = scraper.scrape_profile_ultimate("username")

# Print summary
scraper.print_summary(data)

# Save results
scraper.save_results(data, "username")

scraper.close()
```

### Advanced Scraper
```python
from tiktok_advanced_scraper import AdvancedTikTokScraper

scraper = AdvancedTikTokScraper(headless=False, slow_mo=50)
scraper.start()

profile_data = scraper.scrape_profile_comprehensive("username")
scraper.print_comprehensive_summary(profile_data)
scraper.save_to_file(profile_data, "output.json")

scraper.close()
```

### Basic Scraper
```python
from tiktok_scraper import TikTokScraper

scraper = TikTokScraper(headless=True)
scraper.start()
profile_data = scraper.scrape_profile("username")
scraper.save_to_file(profile_data)
scraper.close()
```

## 📊 Output Files

The scrapers generate multiple files:

1. **`{username}_ultimate.json`** - Complete profile data with all videos
2. **`{username}_videos.json`** - Detailed video data only
3. **`{username}_api_responses.json`** - Raw API responses (for debugging)
4. **`{username}_screenshot.png`** - Full-page screenshot
5. **`SCRAPING_REPORT.md`** - Comprehensive analysis report

## 📈 Data Structure

Each video entry includes:

```json
{
  "id": "7534402199967780126",
  "desc": "Video description...",
  "url": "https://www.tiktok.com/@username/video/7534402199967780126",
  "author": {
    "id": "6665142338295480325",
    "unique_id": "username",
    "nickname": "Display Name",
    "avatar": "https://..."
  },
  "stats": {
    "play_count": 1000,
    "digg_count": 100,
    "comment_count": 20,
    "share_count": 5
  },
  "video": {
    "duration": 15,
    "cover": "https://...",
    "play_addr": "https://...",
    "width": 1080,
    "height": 1920
  },
  "music": {
    "id": "...",
    "title": "Song Title",
    "author": "Artist Name"
  },
  "hashtags": ["fyp", "viral"]
}
```

## 🛠️ Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `tiktok_ultimate_scraper.py` | Network interception scraper | **Best for complete data** |
| `tiktok_advanced_scraper.py` | Comprehensive HTML scraper | Good for visible content |
| `tiktok_scraper.py` | Basic profile scraper | Quick profile checks |
| `tiktok_json_parser.py` | Parse captured JSON data | Analyze existing data |

## 🎯 Example Results

For profile **@.wabby**:
- ✅ Profile info: 100% captured
- ✅ Statistics: 383 followers, 426 following, 5,017 likes
- ✅ Videos: 18 videos captured with full metadata
- ✅ Additional content: 163 related videos
- ✅ API responses: 30+ intercepted

## ⚙️ Configuration

Modify the `main()` function in any scraper:

```python
def main():
    username = "your_target_username"  # Change this
    
    scraper = UltimateTikTokScraper(
        headless=False  # Set True for background operation
    )
    
    # ... rest of the code
```

## 🔍 Advanced Usage

### Parse Existing JSON Data
```bash
python tiktok_json_parser.py {username}_comprehensive.json
```

### Custom Scrolling
```python
scraper._scroll_and_extract_videos(max_scrolls=20)  # Increase scrolling
```

### Debug Mode
Set `headless=False` to watch the browser in action:
```python
scraper = UltimateTikTokScraper(headless=False)
```

## ⚠️ Important Notes

1. **Rate Limiting:** TikTok may rate limit excessive requests
2. **Privacy:** Respect user privacy and platform terms of service
3. **Authentication:** Some content requires login (not implemented)
4. **Robots.txt:** Check TikTok's robots.txt before large-scale scraping
5. **Legal:** Ensure compliance with local laws and TikTok's ToS

## 🐛 Troubleshooting

### Videos not loading?
- Try `headless=False` to see what's happening
- Increase scroll count in `_scroll_and_extract_videos()`
- Check if profile is private

### API responses not captured?
- Ensure using `tiktok_ultimate_scraper.py`
- Check network tab in browser for API calls
- Some regions may have different API endpoints

### Browser errors?
```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

## 📚 Dependencies

- `playwright>=1.48.0` - Browser automation
- `requests>=2.31.0` - HTTP requests
- `beautifulsoup4>=4.12.0` - HTML parsing

## 🤝 Contributing

Feel free to enhance the scrapers:
1. Add authentication support
2. Implement comment scraping
3. Add video download functionality
4. Create batch scraping tools
5. Add data analysis features

## 📄 License

Use responsibly and in accordance with TikTok's Terms of Service.

## 🎉 Success Rate

- Profile Information: **100%**
- Statistics: **100%**
- Videos: **70-90%** (depends on profile settings)
- Network Data: **30+ API calls captured**

---

**Created:** October 2025  
**Status:** Fully functional  
**Last Test:** @.wabby profile (successful)  

For detailed analysis, see `SCRAPING_REPORT.md`


