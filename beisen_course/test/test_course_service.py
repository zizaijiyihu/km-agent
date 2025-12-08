import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure project root on sys.path when running this test directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from beisen_course import course_service


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


class CourseServiceTests(unittest.TestCase):
    @patch("beisen_course.course_service.requests.post")
    def test_get_course_list_success(self, mock_post):
        # First call returns access_token, second returns course list
        mock_post.side_effect = [
            _FakeResponse(200, {"access_token": "token-123"}),
            _FakeResponse(
                200,
                {
                    "data": {
                        "items": [
                            {"title": "Demo", "courseId": "1", "description": "sample"}
                        ],
                        "totalCount": 1,
                    }
                },
            ),
        ]

        result = course_service.get_course_list(page_index=2, page_size=5)

        # Print fetched course list for visibility when running the test
        print("Courses returned:", result["data"])

        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["page_index"], 2)
        self.assertEqual(result["page_size"], 5)


if __name__ == "__main__":
    unittest.main()
