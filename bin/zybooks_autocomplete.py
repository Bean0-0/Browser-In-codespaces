#!/usr/bin/env python3
"""
Zybooks Assignment Auto-Completion Script
Automatically completes participation activities in Zybooks using captured traffic data
"""

import json
import sqlite3
import requests
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse


class ZybooksAutomation:
    """Automate Zybooks assignment completion using captured authentication"""
    
    def __init__(self, db_path: str = "data/traffic.db"):
        self.db_path = db_path
        self.auth_token = None
        self.zybook_code = None
        self.session = requests.Session()
        self.base_url = "https://zyserver.zybooks.com/v1"
        
    def extract_auth_from_traffic(self) -> bool:
        """Extract authentication token from captured traffic"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find most recent authenticated request to zybooks
        cursor.execute("""
            SELECT headers, body FROM requests 
            WHERE host LIKE '%zyserver.zybooks.com%' 
            AND method = 'POST'
            AND headers LIKE '%authorization%'
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("❌ No authenticated zybooks requests found in traffic")
            return False
        
        # Parse headers to get auth token
        headers = json.loads(row['headers'])
        auth_header = headers.get('authorization', '')
        
        if auth_header.startswith('Bearer '):
            self.auth_token = auth_header.split('Bearer ')[1]
            print(f"✅ Extracted auth token: {self.auth_token[:20]}...")
        else:
            print("❌ No valid Bearer token found")
            return False
        
        # Extract zybook code from request body
        if row['body']:
            try:
                body = json.loads(row['body'])
                self.zybook_code = body.get('zybook_code')
                if self.zybook_code:
                    print(f"✅ Extracted zybook code: {self.zybook_code}")
            except:
                pass
        
        # Set up session headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://learn.zybooks.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        return True
    
    def get_incomplete_activities(self) -> List[Dict]:
        """Query traffic database to find content resources that can be completed"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find all content resources accessed
        cursor.execute("""
            SELECT DISTINCT 
                url,
                body,
                response_body
            FROM requests 
            WHERE host LIKE '%zyserver.zybooks.com%' 
            AND url LIKE '%/content_resource/%/activity%'
            AND method = 'POST'
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        seen_resources = set()
        
        for row in rows:
            # Extract content_resource ID from URL
            match = re.search(r'/content_resource/(\d+)/', row['url'])
            if match:
                resource_id = match.group(1)
                
                if resource_id in seen_resources:
                    continue
                seen_resources.add(resource_id)
                
                # Parse the request to see completion status
                try:
                    body = json.loads(row['body'])
                    is_complete = body.get('complete', False)
                    part = body.get('part', 0)
                    
                    activities.append({
                        'resource_id': resource_id,
                        'part': part,
                        'completed': is_complete,
                        'url': row['url']
                    })
                except:
                    pass
        
        return activities
    
    def complete_activity(self, resource_id: str, part: int = 0, 
                         event_type: str = "animation completely watched") -> bool:
        """
        Mark an activity as complete
        
        Args:
            resource_id: The content resource ID
            part: The part number (usually 0)
            event_type: Type of completion event
        """
        url = f"{self.base_url}/content_resource/{resource_id}/activity"
        
        payload = {
            "part": part,
            "complete": True,
            "metadata": json.dumps({
                "event": event_type,
                "isTrusted": {"isTrusted": False},
                "computerTime": datetime.utcnow().isoformat() + "Z"
            }),
            "zybook_code": self.zybook_code
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Completed resource {resource_id} (part {part})")
                    return True
                else:
                    print(f"⚠️  Resource {resource_id}: {result}")
                    return False
            else:
                print(f"❌ Failed to complete {resource_id}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error completing {resource_id}: {e}")
            return False
    
    def auto_complete_all(self, delay: float = 1.0, dry_run: bool = False) -> Tuple[int, int]:
        """
        Automatically complete all incomplete activities
        
        Args:
            delay: Delay between requests (seconds)
            dry_run: If True, only show what would be done
            
        Returns:
            Tuple of (successful, failed) counts
        """
        if not self.auth_token:
            if not self.extract_auth_from_traffic():
                return (0, 0)
        
        activities = self.get_incomplete_activities()
        
        if not activities:
            print("ℹ️  No activities found in traffic data")
            return (0, 0)
        
        incomplete = [a for a in activities if not a['completed']]
        
        print(f"\n📊 Found {len(activities)} total activities")
        print(f"   • {len(incomplete)} incomplete")
        print(f"   • {len(activities) - len(incomplete)} already complete")
        
        if dry_run:
            print("\n🔍 DRY RUN - Would complete:")
            for activity in incomplete[:10]:
                print(f"   • Resource {activity['resource_id']} (part {activity['part']})")
            if len(incomplete) > 10:
                print(f"   ... and {len(incomplete) - 10} more")
            return (0, 0)
        
        print(f"\n🚀 Starting auto-completion with {delay}s delay...")
        
        successful = 0
        failed = 0
        
        for i, activity in enumerate(incomplete, 1):
            print(f"\n[{i}/{len(incomplete)}] Processing resource {activity['resource_id']}...")
            
            if self.complete_activity(activity['resource_id'], activity['part']):
                successful += 1
            else:
                failed += 1
            
            # Rate limiting
            if i < len(incomplete):
                time.sleep(delay)
        
        return (successful, failed)
    
    def complete_by_resource_ids(self, resource_ids: List[str], delay: float = 1.0) -> Tuple[int, int]:
        """Complete specific resources by ID"""
        if not self.auth_token:
            if not self.extract_auth_from_traffic():
                return (0, 0)
        
        successful = 0
        failed = 0
        
        print(f"\n🚀 Completing {len(resource_ids)} specific resources...")
        
        for i, resource_id in enumerate(resource_ids, 1):
            print(f"\n[{i}/{len(resource_ids)}] Processing resource {resource_id}...")
            
            if self.complete_activity(resource_id):
                successful += 1
            else:
                failed += 1
            
            if i < len(resource_ids):
                time.sleep(delay)
        
        return (successful, failed)
    
    def show_activity_summary(self):
        """Display summary of activities from traffic"""
        activities = self.get_incomplete_activities()
        
        if not activities:
            print("ℹ️  No activities found in traffic data")
            return
        
        print(f"\n📊 Activity Summary")
        print("━" * 80)
        print(f"{'Resource ID':<15} {'Part':<6} {'Status':<12} {'URL'}")
        print("━" * 80)
        
        for activity in activities[:20]:
            status = "✅ Complete" if activity['completed'] else "⏳ Incomplete"
            url_short = activity['url'][:50] + "..." if len(activity['url']) > 50 else activity['url']
            print(f"{activity['resource_id']:<15} {activity['part']:<6} {status:<12} {url_short}")
        
        if len(activities) > 20:
            print(f"\n... and {len(activities) - 20} more activities")
        
        incomplete_count = sum(1 for a in activities if not a['completed'])
        complete_count = len(activities) - incomplete_count
        
        print("\n" + "━" * 80)
        print(f"Total: {len(activities)} | Complete: {complete_count} | Incomplete: {incomplete_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Zybooks Assignment Auto-Completion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show summary of activities
  %(prog)s summary
  
  # Auto-complete all incomplete activities (dry run)
  %(prog)s auto --dry-run
  
  # Auto-complete all incomplete activities
  %(prog)s auto
  
  # Complete with custom delay
  %(prog)s auto --delay 2.0
  
  # Complete specific resources
  %(prog)s complete 115060266 115060274 115060276
  
  # Extract and show auth token
  %(prog)s auth

Note: This tool uses authentication tokens from captured traffic.
Make sure you've browsed Zybooks with the proxy running first.
        """
    )
    
    parser.add_argument('command', choices=['summary', 'auto', 'complete', 'auth'],
                       help='Command to execute')
    parser.add_argument('resource_ids', nargs='*', 
                       help='Resource IDs to complete (for "complete" command)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--db', default='data/traffic.db',
                       help='Path to traffic database')
    
    args = parser.parse_args()
    
    automator = ZybooksAutomation(db_path=args.db)
    
    try:
        if args.command == 'auth':
            if automator.extract_auth_from_traffic():
                print(f"\n✅ Authentication extracted successfully")
                print(f"Token: {automator.auth_token[:30]}...")
                print(f"Zybook: {automator.zybook_code}")
            else:
                print("\n❌ Failed to extract authentication")
        
        elif args.command == 'summary':
            automator.show_activity_summary()
        
        elif args.command == 'auto':
            successful, failed = automator.auto_complete_all(
                delay=args.delay,
                dry_run=args.dry_run
            )
            
            if not args.dry_run:
                print(f"\n{'='*80}")
                print(f"✨ Completion Summary")
                print(f"{'='*80}")
                print(f"✅ Successful: {successful}")
                print(f"❌ Failed: {failed}")
                print(f"📊 Total: {successful + failed}")
        
        elif args.command == 'complete':
            if not args.resource_ids:
                print("❌ Error: Please provide resource IDs to complete")
                return
            
            successful, failed = automator.complete_by_resource_ids(
                args.resource_ids,
                delay=args.delay
            )
            
            print(f"\n{'='*80}")
            print(f"✨ Completion Summary")
            print(f"{'='*80}")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
