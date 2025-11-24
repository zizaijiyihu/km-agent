#!/usr/bin/env python3
"""
API Testing Script for Knowledge Management Agent API

Tests all available endpoints:
1. Health check
2. Get documents list
3. Upload PDF with SSE
4. Chat with agent (SSE)
5. Update document visibility
6. Get document content
7. Delete document
"""

import requests
import json
import time
import os
import sys


# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
DEFAULT_OWNER = os.getenv('DEFAULT_OWNER', 'hu')
TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), '居住证办理.pdf')


class Colors:
    """Terminal colors for output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def test_health_check():
    """Test 1: Health check endpoint"""
    print_header("Test 1: Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Response: {json.dumps(data, indent=2)}")

            if data.get('status') == 'healthy':
                print_success("Health check passed!")
                return True
            else:
                print_error("Service not healthy")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False


def test_get_documents():
    """Test 2: Get documents list"""
    print_header("Test 2: Get Documents List")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/documents",
            params={'owner': DEFAULT_OWNER},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Owner: {data.get('owner')}")
            print_info(f"Document count: {data.get('count')}")

            if data.get('documents'):
                print_info("Documents:")
                for doc in data['documents'][:5]:  # Show first 5
                    print(f"  - {doc['filename']} (size: {doc['file_size']} bytes)")

                if len(data['documents']) > 5:
                    print(f"  ... and {len(data['documents']) - 5} more")
            else:
                print_warning("No documents found")

            print_success("Get documents list passed!")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Get documents failed: {str(e)}")
        return False


def test_upload_pdf():
    """Test 3: Upload PDF with SSE progress"""
    print_header("Test 3: Upload PDF with SSE")

    if not os.path.exists(TEST_PDF_PATH):
        print_error(f"Test PDF not found: {TEST_PDF_PATH}")
        return False

    try:
        print_info(f"Uploading: {os.path.basename(TEST_PDF_PATH)}")
        print_info(f"File size: {os.path.getsize(TEST_PDF_PATH)} bytes")

        # Prepare multipart form data
        with open(TEST_PDF_PATH, 'rb') as f:
            files = {'file': (os.path.basename(TEST_PDF_PATH), f, 'application/pdf')}
            data = {
                'owner': DEFAULT_OWNER,
                'is_public': '0'
            }

            # Stream SSE response
            response = requests.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                data=data,
                stream=True,
                timeout=300
            )

        if response.status_code == 200:
            print_success("Upload started, receiving progress updates...")

            last_stage = None
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])
                            stage = event_data.get('stage')

                            if stage != last_stage:
                                if stage == 'error':
                                    print_error(f"Error: {event_data.get('error')}")
                                    return False
                                else:
                                    print_info(f"Stage: {stage} ({event_data.get('progress_percent', 0)}%)")
                                    if event_data.get('message'):
                                        print(f"  {event_data['message']}")

                                last_stage = stage

                            # Check if completed
                            if stage == 'completed':
                                print_success("Upload and vectorization completed!")
                                return True

                        except json.JSONDecodeError:
                            print_warning(f"Failed to parse SSE data: {line_str}")

            print_error("Upload stream ended without completion")
            return False
        else:
            print_error(f"Upload failed with status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Upload test failed: {str(e)}")
        return False


def test_chat():
    """Test 4: Chat with agent using SSE"""
    print_header("Test 4: Chat with Agent")

    try:
        test_message = "居住证办理需要什么材料？"
        print_info(f"Question: {test_message}")

        payload = {
            'message': test_message,
            'history': None
        }

        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=60
        )

        if response.status_code == 200:
            print_success("Chat started, receiving response...")
            print(f"\n{Colors.OKCYAN}Agent Response:{Colors.ENDC}")

            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])
                            event_type = event_data.get('type')

                            if event_type == 'content':
                                # data field is directly a string, not an object
                                content = event_data.get('data', '')
                                print(content, end='', flush=True)
                                full_response += content
                            elif event_type == 'tool_call':
                                # data field contains tool information
                                data = event_data.get('data', {})
                                tool_name = data.get('tool_name') if isinstance(data, dict) else str(data)
                                print(f"\n{Colors.WARNING}[Tool: {tool_name}]{Colors.ENDC}\n", flush=True)
                            elif event_type == 'done':
                                print("\n")
                                print_success("Chat completed!")
                                return True
                            elif event_type == 'error':
                                # data field contains error information
                                data = event_data.get('data', {})
                                error_msg = data.get('error') if isinstance(data, dict) else str(data)
                                print_error(f"\nError: {error_msg}")
                                return False

                        except json.JSONDecodeError:
                            print_warning(f"Failed to parse SSE data")

            if full_response:
                print_success("Chat test passed!")
                return True
            else:
                print_error("No response received")
                return False
        else:
            print_error(f"Chat failed with status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Chat test failed: {str(e)}")
        return False


def test_update_visibility():
    """Test 5: Update document visibility"""
    print_header("Test 5: Update Document Visibility")

    try:
        test_filename = os.path.basename(TEST_PDF_PATH)

        # Set to public
        print_info(f"Setting {test_filename} to public...")
        response = requests.put(
            f"{API_BASE_URL}/api/documents/{test_filename}/visibility",
            params={'owner': DEFAULT_OWNER},
            json={'is_public': 1},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Response: {json.dumps(data, indent=2)}")

            # Set back to private
            print_info(f"Setting {test_filename} back to private...")
            response2 = requests.put(
                f"{API_BASE_URL}/api/documents/{test_filename}/visibility",
                params={'owner': DEFAULT_OWNER},
                json={'is_public': 0},
                timeout=10
            )

            if response2.status_code == 200:
                print_success("Update visibility test passed!")
                return True
            else:
                print_error(f"Failed to set back to private: {response2.status_code}")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Update visibility test failed: {str(e)}")
        return False


def test_get_document_content():
    """Test 6: Get document content"""
    print_header("Test 6: Get Document Content")

    try:
        test_filename = os.path.basename(TEST_PDF_PATH)
        print_info(f"Requesting content for: {test_filename}")

        response = requests.get(
            f"{API_BASE_URL}/api/documents/{test_filename}/content",
            params={'owner': DEFAULT_OWNER},
            timeout=30
        )

        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print_info(f"Content-Type: {response.headers.get('Content-Type')}")
            print_info(f"Content size: {len(response.content)} bytes")

            if response.headers.get('Content-Type') == 'application/pdf':
                print_success("Get document content test passed!")
                return True
            else:
                print_error("Unexpected content type")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Get document content test failed: {str(e)}")
        return False


def test_delete_document():
    """Test 7: Delete document"""
    print_header("Test 7: Delete Document")

    try:
        test_filename = os.path.basename(TEST_PDF_PATH)
        print_warning(f"Deleting: {test_filename}")

        response = requests.delete(
            f"{API_BASE_URL}/api/documents/{test_filename}",
            params={'owner': DEFAULT_OWNER},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            print_success("Delete document test passed!")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Delete document test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}API Testing Script{Colors.ENDC}")
    print(f"Target: {Colors.OKBLUE}{API_BASE_URL}{Colors.ENDC}")
    print(f"Owner: {Colors.OKBLUE}{DEFAULT_OWNER}{Colors.ENDC}")
    print(f"Test PDF: {Colors.OKBLUE}{TEST_PDF_PATH}{Colors.ENDC}")

    # Check if test file exists
    if not os.path.exists(TEST_PDF_PATH):
        print_error(f"\nTest PDF not found: {TEST_PDF_PATH}")
        print_info("Please ensure 居住证办理.pdf is in the test directory")
        sys.exit(1)

    # Run tests
    results = []

    # Test 1: Health check
    results.append(('Health Check', test_health_check()))
    time.sleep(1)

    # Test 2: Get documents
    results.append(('Get Documents', test_get_documents()))
    time.sleep(1)

    # Test 3: Upload PDF
    results.append(('Upload PDF', test_upload_pdf()))
    time.sleep(2)

    # Test 4: Chat
    results.append(('Chat', test_chat()))
    time.sleep(1)

    # Test 5: Update visibility
    results.append(('Update Visibility', test_update_visibility()))
    time.sleep(1)

    # Test 6: Get document content
    results.append(('Get Document Content', test_get_document_content()))
    time.sleep(1)

    # Test 7: Delete document
    results.append(('Delete Document', test_delete_document()))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.OKGREEN}PASSED{Colors.ENDC}" if result else f"{Colors.FAIL}FAILED{Colors.ENDC}"
        print(f"{test_name:.<50} {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")

    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Some tests failed{Colors.ENDC}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
        sys.exit(130)
