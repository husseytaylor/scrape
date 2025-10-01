#!/usr/bin/env python3
"""
TikTok JSON Parser
Extracts all possible data from the captured JSON structures
"""

import json
import sys
from typing import Dict, List


def parse_user_videos_from_json(json_data: Dict) -> List[Dict]:
    """
    Try to extract video data from various JSON structures
    """
    videos = []
    
    # Try UNIVERSAL_DATA
    if 'UNIVERSAL_DATA' in json_data:
        print("Parsing UNIVERSAL_DATA...")
        try:
            default_scope = json_data['UNIVERSAL_DATA'].get('__DEFAULT_SCOPE__', {})
            
            # Check for video list in user detail
            user_detail = default_scope.get('webapp.user-detail', {})
            if 'itemList' in user_detail and user_detail['itemList']:
                print(f"  ✓ Found itemList with {len(user_detail['itemList'])} videos")
                videos.extend(parse_video_list(user_detail['itemList']))
            
            # Check for video-detail
            video_detail = default_scope.get('webapp.video-detail', {})
            if 'itemInfo' in video_detail:
                print(f"  ✓ Found itemInfo")
                videos.append(parse_video_item(video_detail['itemInfo']))
            
            # Check all keys for video data
            for key, value in default_scope.items():
                if isinstance(value, dict):
                    if 'itemList' in value and isinstance(value['itemList'], list):
                        print(f"  ✓ Found itemList in {key}")
                        videos.extend(parse_video_list(value['itemList']))
                    if 'itemInfo' in value and isinstance(value['itemInfo'], dict):
                        print(f"  ✓ Found itemInfo in {key}")
                        videos.append(parse_video_item(value['itemInfo']))
        
        except Exception as e:
            print(f"  ⚠️  Error parsing UNIVERSAL_DATA: {e}")
    
    # Try SIGI_STATE
    if 'SIGI_STATE' in json_data:
        print("Parsing SIGI_STATE...")
        try:
            sigi = json_data['SIGI_STATE']
            
            # Look for ItemModule
            if 'ItemModule' in sigi:
                print(f"  ✓ Found ItemModule")
                item_module = sigi['ItemModule']
                for item_id, item_data in item_module.items():
                    videos.append(parse_video_item({'itemStruct': item_data}))
            
            # Look for UserModule
            if 'UserModule' in sigi:
                user_module = sigi['UserModule']
                if 'users' in user_module:
                    for user_id, user_data in user_module['users'].items():
                        if 'itemList' in user_data:
                            videos.extend(parse_video_list(user_data['itemList']))
        
        except Exception as e:
            print(f"  ⚠️  Error parsing SIGI_STATE: {e}")
    
    # Try NEXT_DATA
    if 'NEXT_DATA' in json_data:
        print("Parsing NEXT_DATA...")
        try:
            # Navigate through Next.js data structure
            props = json_data['NEXT_DATA'].get('props', {})
            page_props = props.get('pageProps', {})
            
            if 'items' in page_props:
                videos.extend(parse_video_list(page_props['items']))
        
        except Exception as e:
            print(f"  ⚠️  Error parsing NEXT_DATA: {e}")
    
    # Remove duplicates
    unique_videos = []
    seen_ids = set()
    
    for video in videos:
        video_id = video.get('id') or video.get('video_id')
        if video_id and video_id not in seen_ids:
            seen_ids.add(video_id)
            unique_videos.append(video)
    
    return unique_videos


def parse_video_list(item_list: List) -> List[Dict]:
    """Parse a list of video items"""
    videos = []
    
    for item in item_list:
        try:
            video = parse_video_item({'itemStruct': item} if 'itemStruct' not in item else item)
            if video:
                videos.append(video)
        except:
            continue
    
    return videos


def parse_video_item(item_data: Dict) -> Dict:
    """Parse a single video item"""
    video = {}
    
    try:
        # Get the item structure
        item = item_data.get('itemStruct') or item_data.get('itemInfo') or item_data
        
        # Basic info
        video['id'] = item.get('id')
        video['desc'] = item.get('desc')
        video['create_time'] = item.get('createTime')
        
        # Author info
        if 'author' in item:
            author = item['author']
            video['author'] = {
                'id': author.get('id'),
                'unique_id': author.get('uniqueId'),
                'nickname': author.get('nickname'),
                'avatar': author.get('avatarLarger') or author.get('avatarMedium')
            }
        
        # Stats
        if 'stats' in item:
            stats = item['stats']
            video['stats'] = {
                'play_count': stats.get('playCount'),
                'digg_count': stats.get('diggCount'),
                'comment_count': stats.get('commentCount'),
                'share_count': stats.get('shareCount'),
                'download_count': stats.get('downloadCount')
            }
        
        # Video info
        if 'video' in item:
            vid = item['video']
            video['video'] = {
                'duration': vid.get('duration'),
                'ratio': vid.get('ratio'),
                'cover': vid.get('cover') or vid.get('dynamicCover'),
                'download_addr': vid.get('downloadAddr'),
                'play_addr': vid.get('playAddr')
            }
        
        # Music info
        if 'music' in item:
            music = item['music']
            video['music'] = {
                'id': music.get('id'),
                'title': music.get('title'),
                'author_name': music.get('authorName'),
                'play_url': music.get('playUrl')
            }
        
        # Challenges/hashtags
        if 'challenges' in item:
            video['challenges'] = [
                {
                    'id': ch.get('id'),
                    'title': ch.get('title'),
                    'desc': ch.get('desc')
                }
                for ch in item['challenges']
            ]
        
        # URL
        if video.get('id') and video.get('author'):
            video['url'] = f"https://www.tiktok.com/@{video['author'].get('unique_id')}/video/{video['id']}"
        elif video.get('id'):
            video['url'] = f"https://www.tiktok.com/video/{video['id']}"
    
    except Exception as e:
        print(f"    ⚠️  Error parsing video: {e}")
    
    return video


def parse_comprehensive_json(filename: str):
    """Parse the comprehensive JSON file"""
    print(f"\n🔍 Parsing {filename}...")
    print("="*70)
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Get raw JSON data
    raw_json = data.get('raw_json_data', {})
    
    if not raw_json:
        print("❌ No raw JSON data found in file")
        return
    
    # Parse videos
    print("\n📹 Extracting video data from JSON structures...\n")
    videos = parse_user_videos_from_json(raw_json)
    
    print(f"\n{'='*70}")
    print(f"✅ FOUND {len(videos)} VIDEOS IN JSON DATA")
    print("="*70)
    
    if videos:
        # Update the data
        data['videos_from_json'] = videos
        
        # Print summary
        print("\n📊 VIDEO SUMMARY:\n")
        for i, video in enumerate(videos[:10], 1):
            print(f"{i}. Video ID: {video.get('id')}")
            print(f"   Description: {video.get('desc', 'N/A')[:70]}...")
            if video.get('stats'):
                stats = video['stats']
                print(f"   Stats: 👁️  {stats.get('play_count', 0):,} plays, "
                      f"❤️  {stats.get('digg_count', 0):,} likes, "
                      f"💬 {stats.get('comment_count', 0):,} comments")
            print(f"   URL: {video.get('url', 'N/A')}")
            print()
        
        if len(videos) > 10:
            print(f"... and {len(videos) - 10} more videos\n")
        
        # Save updated file
        output_filename = filename.replace('.json', '_with_videos.json')
        with open(output_filename, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Updated data saved to: {output_filename}")
        
        # Create a videos-only file
        videos_only_filename = filename.replace('.json', '_videos_only.json')
        with open(videos_only_filename, 'w') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Videos-only data saved to: {videos_only_filename}")
    
    else:
        print("\n⚠️  No videos found in JSON structures")
        print("\nAvailable JSON keys:")
        for key in raw_json.keys():
            print(f"  • {key}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = ".wabby_comprehensive.json"
    
    parse_comprehensive_json(filename)

