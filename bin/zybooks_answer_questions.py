#!/usr/bin/env python3
"""
Zybooks Question Answering - DEMO/EDUCATIONAL ONLY
This demonstrates how Zybooks question submission works.

⚠️ IMPORTANT LIMITATIONS:
- Cannot actually answer questions intelligently
- Can only replay previously captured correct answers
- Demonstrates API mechanics for educational purposes
- Requires you to have answered questions with proxy running

For actual learning, complete assignments manually!
"""

import json
import sqlite3
import requests
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse


class ZybooksQuestionAnswerer:
    """Educational demo of Zybooks question answering API"""
    
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
            print("❌ No authenticated zybooks requests found")
            return False
        
        headers = json.loads(row['headers'])
        auth_header = headers.get('authorization', '')
        
        if auth_header.startswith('Bearer '):
            self.auth_token = auth_header.split('Bearer ')[1]
            print(f"✅ Extracted auth token: {self.auth_token[:20]}...")
        else:
            return False
        
        if row['body']:
            try:
                body = json.loads(row['body'])
                self.zybook_code = body.get('zybook_code')
                if self.zybook_code:
                    print(f"✅ Extracted zybook code: {self.zybook_code}")
            except:
                pass
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://learn.zybooks.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        return True
    
    def find_answered_questions(self) -> List[Dict]:
        """Find questions that were answered in captured traffic"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find POST requests with answers
        cursor.execute("""
            SELECT 
                url,
                body,
                response_body,
                response_status,
                timestamp
            FROM requests 
            WHERE host LIKE '%zyserver.zybooks.com%' 
            AND url LIKE '%/content_resource/%/activity%'
            AND method = 'POST'
            AND body LIKE '%answer%'
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        questions = []
        
        for row in rows:
            match = re.search(r'/content_resource/(\d+)/', row['url'])
            if not match:
                continue
                
            resource_id = match.group(1)
            
            try:
                body = json.loads(row['body'])
                
                # Check if this has an answer
                if 'answer' in body:
                    answer_data = body.get('answer', '')
                    complete = body.get('complete', False)
                    
                    questions.append({
                        'resource_id': resource_id,
                        'answer': answer_data,
                        'complete': complete,
                        'metadata': body.get('metadata', '{}'),
                        'timestamp': row['timestamp'],
                        'success': row['response_status'] == 200
                    })
            except:
                continue
        
        return questions
    
    def replay_answer(self, resource_id: str, answer: str, 
                     metadata: str = '{}', part: int = 0) -> bool:
        """
        Replay a previously captured answer
        
        ⚠️ This only works if the question hasn't changed!
        """
        url = f"{self.base_url}/content_resource/{resource_id}/activity"
        
        payload = {
            "answer": answer,
            "complete": True,
            "metadata": metadata,
            "part": part,
            "zybook_code": self.zybook_code
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Replayed answer for resource {resource_id}")
                    return True
                else:
                    print(f"⚠️  Resource {resource_id}: {result}")
                    return False
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def show_captured_answers(self):
        """Display answers that were captured from previous sessions"""
        questions = self.find_answered_questions()
        
        if not questions:
            print("\n❌ No answered questions found in captured traffic")
            print("\nTo use this tool:")
            print("  1. Start the proxy: ./bin/start_analyzer.sh")
            print("  2. Answer some questions in Zybooks manually")
            print("  3. Run this tool again to see captured answers")
            return
        
        print(f"\n📊 Captured Answers ({len(questions)} found)")
        print("━" * 80)
        print(f"{'Resource ID':<15} {'Complete':<10} {'Success':<10} {'Preview'}")
        print("━" * 80)
        
        for q in questions[:20]:
            complete = "✅ Yes" if q['complete'] else "⏳ No"
            success = "✅" if q['success'] else "❌"
            
            # Preview the answer
            answer_preview = str(q['answer'])[:50]
            if len(str(q['answer'])) > 50:
                answer_preview += "..."
            
            print(f"{q['resource_id']:<15} {complete:<10} {success:<10} {answer_preview}")
        
        if len(questions) > 20:
            print(f"\n... and {len(questions) - 20} more answers")
        
        print("\n" + "━" * 80)
        print(f"ℹ️  These are answers YOU submitted previously")
        print(f"ℹ️  Can only replay if questions haven't changed")
    
    def explain_limitations(self):
        """Explain why this tool has limitations"""
        print("\n" + "=" * 80)
        print("⚠️  IMPORTANT: Why This Tool Cannot Truly 'Answer' Questions")
        print("=" * 80)
        print()
        print("This tool can ONLY:")
        print("  ✅ Replay answers YOU previously submitted")
        print("  ✅ Demonstrate the API mechanics")
        print("  ✅ Show how question submission works")
        print()
        print("This tool CANNOT:")
        print("  ❌ Generate correct answers to new questions")
        print("  ❌ Solve coding challenges automatically")
        print("  ❌ Understand question content")
        print("  ❌ Work if questions change or randomize")
        print()
        print("Why?")
        print("  • Questions often have randomized values")
        print("  • Coding challenges require actual code")
        print("  • Multiple choice options may vary")
        print("  • Answer validation happens server-side")
        print()
        print("To actually learn:")
        print("  📚 Read the content")
        print("  💻 Write the code yourself")
        print("  🧠 Understand the concepts")
        print("  ✍️  Answer questions manually")
        print()
        print("This tool is for EDUCATIONAL purposes:")
        print("  🔍 Understanding web APIs")
        print("  🔧 Learning HTTP requests")
        print("  📖 Reverse engineering practice")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Zybooks Question Answering Demo - Educational Only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  EDUCATIONAL DEMO ONLY ⚠️

This tool demonstrates Zybooks question submission API mechanics.
It can ONLY replay answers you previously submitted yourself.

It CANNOT:
  - Generate new correct answers
  - Solve coding problems
  - Answer questions it hasn't seen before

For actual learning, complete assignments manually!

Examples:
  # Show captured answers from your previous sessions
  %(prog)s show
  
  # Explain limitations
  %(prog)s explain
  
  # Check authentication
  %(prog)s auth

Note: You must answer questions manually with the proxy running first!
        """
    )
    
    parser.add_argument('command', 
                       choices=['show', 'explain', 'auth'],
                       help='Command to execute')
    parser.add_argument('--db', default='data/traffic.db',
                       help='Path to traffic database')
    
    args = parser.parse_args()
    
    answerer = ZybooksQuestionAnswerer(db_path=args.db)
    
    try:
        if args.command == 'explain':
            answerer.explain_limitations()
        
        elif args.command == 'auth':
            if answerer.extract_auth_from_traffic():
                print(f"\n✅ Authentication valid")
            else:
                print("\n❌ Failed to extract authentication")
        
        elif args.command == 'show':
            answerer.show_captured_answers()
            print()
            print("💡 Tip: These answers were captured from YOUR previous submissions")
            print("💡 To capture more, answer questions manually with proxy running")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
