"""
Smoke Tests for AndroidWorld Challenge
These tests verify basic functionality and are run by the CI/CD pipeline
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, Any


class TestSmokeTests:
    """Smoke tests for basic AndroidWorld functionality"""

    @pytest.fixture(scope="class")
    def base_url(self):
        """Get the base URL for testing"""
        return os.getenv("TEST_BASE_URL", "http://localhost:8080")

    @pytest.fixture(scope="class")
    def test_task_data(self):
        """Sample task data for testing"""
        return {
            "task_id": f"smoke_test_{int(time.time())}",
            "task_type": "click_button",
            "target": "test_button",
            "coordinates": {"x": 100, "y": 200},
        }

    def test_health_endpoint(self, base_url):
        """Test that the health endpoint is accessible"""
        response = requests.get(f"{base_url}/health", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_ready_endpoint(self, base_url):
        """Test that the ready endpoint is accessible"""
        response = requests.get(f"{base_url}/ready", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "ready"

    def test_metrics_endpoint(self, base_url):
        """Test that the metrics endpoint is accessible"""
        response = requests.get(f"{base_url}/metrics", timeout=10)
        assert response.status_code == 200

        # Check that it returns Prometheus format
        content = response.text
        assert "# HELP" in content
        assert "# TYPE" in content

    def test_status_endpoint(self, base_url):
        """Test that the status endpoint is accessible"""
        response = requests.get(f"{base_url}/status", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert "service" in data
        assert data["service"] == "androidworld-worker"
        assert "version" in data
        assert "uptime" in data

    def test_trace_endpoint(self, base_url):
        """Test that the trace endpoint is accessible"""
        response = requests.get(f"{base_url}/trace", timeout=10)
        assert response.status_code == 200

        data = response.json()
        assert "service" in data
        assert data["service"] == "androidworld-worker"

    def test_task_execution(self, base_url, test_task_data):
        """Test that tasks can be executed"""
        response = requests.post(
            f"{base_url}/task",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        assert response.status_code == 200

        data = response.json()
        assert "task_id" in data
        assert data["task_id"] == test_task_data["task_id"]
        assert "success" in data
        assert "duration" in data
        assert "timestamp" in data

    def test_invalid_task_data(self, base_url):
        """Test that invalid task data is handled gracefully"""
        invalid_data = {"invalid": "data"}

        response = requests.post(
            f"{base_url}/task",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        # Should either accept the task or return a validation error
        assert response.status_code in [200, 400, 422]

    def test_response_time_health(self, base_url):
        """Test that health endpoint responds quickly"""
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 1000  # Should respond within 1 second

    def test_response_time_ready(self, base_url):
        """Test that ready endpoint responds quickly"""
        start_time = time.time()
        response = requests.get(f"{base_url}/ready", timeout=5)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        assert response_time < 1000  # Should respond within 1 second

    def test_concurrent_requests(self, base_url):
        """Test that the service can handle concurrent requests"""
        import concurrent.futures

        def make_request():
            response = requests.get(f"{base_url}/health", timeout=5)
            return response.status_code

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert all(status == 200 for status in results)

    def test_service_identity(self, base_url):
        """Test that the service identifies itself correctly"""
        response = requests.get(f"{base_url}/status", timeout=10)
        data = response.json()

        # Check service identity
        assert data["service"] == "androidworld-worker"

        # Check environment
        if "environment" in data:
            assert data["environment"] in ["production", "staging", "development"]

        # Check project ID if available
        if "project_id" in data:
            assert isinstance(data["project_id"], str)

    def test_error_handling(self, base_url):
        """Test that the service handles errors gracefully"""
        # Test non-existent endpoint
        response = requests.get(f"{base_url}/nonexistent", timeout=10)
        assert response.status_code == 404

        # Test invalid JSON
        response = requests.post(
            f"{base_url}/task",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        assert response.status_code in [400, 422]

    def test_cors_headers(self, base_url):
        """Test that CORS headers are present"""
        response = requests.get(f"{base_url}/health", timeout=10)

        # Check for CORS headers
        assert "Access-Control-Allow-Origin" in response.headers

    def test_content_type_headers(self, base_url):
        """Test that content type headers are correct"""
        # JSON endpoints should return application/json
        response = requests.get(f"{base_url}/health", timeout=10)
        assert "application/json" in response.headers.get("Content-Type", "")

        # Metrics endpoint should return text/plain
        response = requests.get(f"{base_url}/metrics", timeout=10)
        assert "text/plain" in response.headers.get("Content-Type", "")


class TestIntegrationSmoke:
    """Integration smoke tests that verify end-to-end functionality"""

    @pytest.fixture(scope="class")
    def base_url(self):
        """Get the base URL for testing"""
        return os.getenv("TEST_BASE_URL", "http://localhost:8080")

    def test_full_task_workflow(self, base_url):
        """Test a complete task workflow"""
        # Create a test task
        task_data = {
            "task_id": f"integration_test_{int(time.time())}",
            "task_type": "verify_text",
            "target": "test_element",
            "expected_text": "Test successful",
        }

        # Execute the task
        response = requests.post(
            f"{base_url}/task",
            json=task_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        assert response.status_code == 200

        # Verify the response
        data = response.json()
        assert data["task_id"] == task_data["task_id"]
        assert data["task_type"] == task_data["task_type"]
        assert "success" in data
        assert "duration" in data

        # Check that the task was processed
        assert data["success"] is True

    def test_multiple_task_types(self, base_url):
        """Test multiple different task types"""
        task_types = [
            {
                "task_type": "click_button",
                "target": "button1",
                "coordinates": {"x": 50, "y": 100},
            },
            {"task_type": "input_text", "target": "input1", "text": "test input"},
            {"task_type": "scroll_list", "direction": "down", "distance": 200},
        ]

        for i, task_type_data in enumerate(task_types):
            task_data = {
                "task_id": f"multi_test_{i}_{int(time.time())}",
                **task_type_data,
            }

            response = requests.post(
                f"{base_url}/task",
                json=task_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert data["task_type"] == task_type_data["task_type"]

    def test_service_resilience(self, base_url):
        """Test that the service is resilient to rapid requests"""
        import concurrent.futures

        def make_rapid_requests():
            """Make rapid requests to test resilience"""
            for i in range(5):
                try:
                    response = requests.get(f"{base_url}/health", timeout=2)
                    if response.status_code != 200:
                        return False
                    time.sleep(0.1)  # Small delay between requests
                except:
                    return False
            return True

        # Make rapid requests from multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_rapid_requests) for _ in range(5)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # Most requests should succeed (allow for some failures)
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8  # At least 80% success rate


if __name__ == "__main__":
    # Run smoke tests directly if script is executed
    pytest.main([__file__, "-v"])
