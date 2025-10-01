# TikTok Profile Scraping Report: @.wabby

**Generated:** October 1, 2025  
**Profile:** https://www.tiktok.com/@.wabby

---

## 🎯 Executive Summary

Successfully scraped comprehensive data from TikTok profile @.wabby using advanced network interception techniques. Captured **18 of the user's own videos** plus **163 additional videos** from likes, recommendations, and reposts.

---

## 👤 Profile Information

### Basic Details
- **Username:** .wabby
- **Display Name:** Abs
- **User ID:** 6665142338295480325
- **Bio:** "I'm confused"
- **Verified:** No
- **Private Account:** No

### Statistics
- **Followers:** 383
- **Following:** 426
- **Total Likes:** 5,017
- **Videos Posted:** 26 (profile states)
- **Videos Captured:** 18 (scraped successfully)
- **Friend Count:** 196

---

## 🎬 User's Videos (18 Captured)

### Top Performing Videos

1. **"I MISS @ella AND THE SIP SO MUCHHHHH"**
   - URL: https://www.tiktok.com/@.wabby/video/7249139831060565290
   - Views: 1,404
   - Likes: 121
   - Comments: 4
   - Music: "super freaky girl x luxurious" - xxtristanxo

2. **"That is so messed up (so was the rest of the night!)"**
   - URL: https://www.tiktok.com/@.wabby/video/7227888387045264683
   - Views: 1,332
   - Likes: 117
   - Comments: 2
   - Music: "picture to burn into" - sophsorr

3. **"Happy fourth skanks"**
   - URL: https://www.tiktok.com/@.wabby/video/7252121017680727339
   - Views: 1,296
   - Likes: 126
   - Comments: 1
   - Music: "original sound" - NBC Sports

4. **"Chi town date ending with us missing our stop 🚊"**
   - URL: https://www.tiktok.com/@.wabby/video/7377241602328202538
   - Views: 1,254
   - Likes: 92
   - Comments: 6
   - Music: "misses" - Dominic Fike

5. **"So excited for u to fall in love with this place..."**
   - URL: https://www.tiktok.com/@.wabby/video/7406886250931621166
   - Views: 1,168
   - Likes: 130
   - Comments: 11
   - Hashtags: #zlam
   - Music: "Electric Love" - BØRNS

### Complete Video List

| # | Video ID | Views | Likes | Comments | Shares |
|---|----------|-------|-------|----------|--------|
| 1 | 7534402199967780126 | 840 | 104 | 20 | 0 |
| 2 | 7521530866900716830 | 386 | 28 | 10 | 4 |
| 3 | 7504384112933768478 | 1,142 | 75 | 3 | 1 |
| 4 | 7406886250931621166 | 1,168 | 130 | 11 | 2 |
| 5 | 7377241602328202538 | 1,254 | 92 | 6 | 0 |
| 6 | 7281415959695346990 | 775 | 50 | 2 | 0 |
| 7 | 7255463184998468906 | 1,024 | 85 | 5 | 2 |
| 8 | 7252121017680727339 | 1,296 | 126 | 1 | 3 |
| 9 | 7249139831060565290 | 1,404 | 121 | 4 | 0 |
| 10 | 7227888387045264683 | 1,332 | 117 | 2 | 2 |
| ... | (8 more videos) | ... | ... | ... | ... |

### Video Analytics Summary

- **Total Views:** ~19,000+ (across captured videos)
- **Total Likes:** ~1,600+
- **Total Comments:** ~130+
- **Total Shares:** ~20+
- **Average Engagement Rate:** ~8.5%

### Popular Hashtags Used
- #fyp
- #butter
- #zlam

### Popular Music Tracks
- "Electric Love" - BØRNS
- "September" - Earth, Wind & Fire
- "misses" - Dominic Fike
- "super freaky girl x luxurious" - xxtristanxo

---

## ❤️ Additional Content Captured

### Liked/Recommended/Reposted Videos: 163

The scraper captured an additional 163 videos from:
- Liked videos (if public)
- Recommended content
- Reposted videos
- Algorithmically suggested content

This data includes videos from various creators that the user has interacted with or that TikTok recommends based on the profile.

---

## 🔧 Technical Details

### Scraping Methods Used

1. **Basic HTML Parsing**
   - Extracted visible profile information
   - Parsed meta tags and Open Graph data

2. **Embedded JSON Extraction**
   - Captured `__UNIVERSAL_DATA_FOR_REHYDRATION__` (240KB)
   - Extracted profile statistics and user data

3. **Network Request Interception**
   - Intercepted 30+ API calls
   - Captured responses from:
     - `/api/post/item_list/` (user's videos)
     - `/api/repost/item_list/` (reposted content)
     - `/api/recommend/item_list/` (recommendations)
     - `/api/preload/item_list/` (preloaded content)

4. **Advanced Scrolling Techniques**
   - 25 scroll iterations to trigger lazy loading
   - Tab navigation to access different content sections
   - Progressive loading of video thumbnails and metadata

### Files Generated

1. **`.wabby_ultimate.json`** (163 KB) - Complete profile data
2. **`.wabby_videos.json`** - All 181 captured videos with full metadata
3. **`.wabby_api_responses.json`** - Raw API responses for analysis
4. **`.wabby_ultimate.png`** - Full-page screenshot
5. **`.wabby_initial.png`** - Initial page state screenshot

---

## 📊 Data Structure

Each video entry includes:

```json
{
  "id": "7534402199967780126",
  "desc": "Video description...",
  "url": "https://www.tiktok.com/@.wabby/video/7534402199967780126",
  "author": {
    "id": "6665142338295480325",
    "unique_id": ".wabby",
    "nickname": "Abs",
    "avatar": "https://..."
  },
  "stats": {
    "play_count": 840,
    "digg_count": 104,
    "comment_count": 20,
    "share_count": 0
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

---

## 🚀 Scraping Tools Created

### 1. `tiktok_scraper.py`
Basic scraper with HTML parsing and embedded JSON extraction.

### 2. `tiktok_advanced_scraper.py`
Enhanced scraper with tab navigation and comprehensive data extraction.

### 3. `tiktok_ultimate_scraper.py` ⭐ **RECOMMENDED**
Ultimate solution with network request interception to capture API responses.

### 4. `tiktok_json_parser.py`
Utility to parse and analyze captured JSON data structures.

---

## 💡 Key Insights

1. **Profile Activity:**
   - Active user with 26 videos posted
   - Moderate engagement (383 followers, 5K+ total likes)
   - Content focused on lifestyle, friends, and social activities

2. **Content Performance:**
   - Average views per video: ~1,000
   - Best performing content relates to friends and social events
   - Consistent engagement across videos

3. **Content Style:**
   - Mix of lifestyle vlogs and friend hangouts
   - Uses popular music tracks
   - Minimal hashtag usage (2-3 per video)
   - Frequent mentions/tags of friends

4. **Scraping Challenges:**
   - Videos not immediately visible in DOM
   - Requires network interception to capture full data
   - Some videos may be hidden/deleted (expected 26, captured 18)
   - Liked videos section may be private

---

## ⚠️ Limitations & Notes

1. **Missing Videos:** Captured 18 out of 26 stated videos. Possible reasons:
   - Some videos may be deleted
   - Some may be private or draft
   - API pagination may not have loaded all content

2. **Data Accuracy:** All data accurate as of scraping timestamp. TikTok metrics update in real-time.

3. **Liked Videos:** Unable to determine if liked videos are private or if they're included in the "other videos" capture.

4. **Comments:** Individual video comments were not scraped (would require separate API calls per video).

5. **Ethical Considerations:** All scraped data is publicly available. Respect user privacy and TikTok's Terms of Service.

---

## 📝 Recommendations

### For Further Analysis:
1. Scrape comments for sentiment analysis
2. Track follower growth over time
3. Analyze posting patterns (times, days)
4. Compare engagement rates with similar profiles

### For Enhanced Scraping:
1. Implement authentication for private content access
2. Add retry logic for failed API calls
3. Implement rate limiting to avoid detection
4. Add proxy rotation for large-scale scraping
5. Schedule periodic scrapes to track changes

---

## ✅ Success Metrics

- ✅ Profile information: **100% captured**
- ✅ Statistics: **100% captured**
- ✅ Videos: **69% captured** (18/26)
- ✅ Video metadata: **100% captured** (for available videos)
- ✅ Network API data: **30+ requests intercepted**
- ✅ Additional content: **163 related videos captured**

---

## 🎉 Conclusion

Successfully implemented a comprehensive TikTok scraping solution that uses network request interception to capture data that isn't directly visible in the page HTML. The ultimate scraper proved most effective, capturing detailed information about 18 videos along with 163 additional videos from various sources.

All data has been saved in structured JSON format for further analysis, and multiple scraping tools have been created for different use cases and complexity levels.

---

**Tools Location:** `/Users/taylorhussey/Firecrawl/`  
**Data Files:** All `.json` and `.png` files in the same directory  
**Primary Contact:** Run `python tiktok_ultimate_scraper.py` to re-scrape or modify `username` variable for different profiles.

