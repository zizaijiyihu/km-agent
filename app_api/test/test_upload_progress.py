#!/usr/bin/env python3
"""
Test script for /api/upload endpoint SSE progress
Tests the Server-Sent Events stream from PDF upload API
"""

import requests
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_upload_sse_progress():
    """Test upload endpoint and print all SSE progress events"""
    
    # Use the test PDF file
    pdf_path = os.path.join(os.path.dirname(__file__), "金山集团及金山云公司介绍.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"Error: Test PDF not found at {pdf_path}")
        return
    
    print(f"Testing upload with: {os.path.basename(pdf_path)}")
    print(f"File size: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB")
    print("=" * 80)
    print()
    
    # Prepare the upload
    url = "http://localhost:5000/api/upload"
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
        data = {'is_public': '0'}
        
        # Make request with stream=True to handle SSE
        try:
            response = requests.post(url, files=files, data=data, stream=True)
            
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                print(response.text)
                return
            
            print("SSE Stream Events:")
            print("-" * 80)
            
            event_count = 0
            buffer = ""
            
            # Read SSE stream
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        
                        if line.startswith('data: '):
                            event_count += 1
                            data_str = line[6:]  # Remove 'data: ' prefix
                            
                            try:
                                data = json.loads(data_str)
                                
                                # Print formatted event
                                print(f"\nEvent #{event_count}:")
                                print(f"  Stage: {data.get('stage', 'N/A')}")
                                print(f"  Message: {data.get('message', 'N/A')}")
                                print(f"  Current Step: {data.get('current_step', 'N/A')}")
                                print(f"  Progress: {data.get('progress_percent', 0):.1f}%")
                                print(f"  Page: {data.get('current_page', 0)}/{data.get('total_pages', 0)}")
                                
                                if data.get('error'):
                                    print(f"  ERROR: {data['error']}")
                                
                                # Check if completed
                                if data.get('stage') == 'completed':
                                    print("\n" + "=" * 80)
                                    print("✓ Upload completed successfully!")
                                    if 'data' in data:
                                        result_data = data['data']
                                        print(f"  Filename: {result_data.get('filename')}")
                                        print(f"  Total pages: {result_data.get('total_pages')}")
                                        print(f"  Processed pages: {result_data.get('processed_pages')}")
                                    break
                                    
                                elif data.get('stage') == 'error':
                                    print("\n" + "=" * 80)
                                    print("✗ Upload failed!")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"Failed to parse JSON: {e}")
                                print(f"Raw data: {data_str}")
            
            print("\n" + "=" * 80)
            print(f"Total events received: {event_count}")
            
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to server. Is it running on http://localhost:5000?")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_upload_sse_progress()
