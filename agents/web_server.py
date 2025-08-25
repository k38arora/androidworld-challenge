"""
Web Server for AndroidWorld Worker
Provides health checks, readiness probes, and observability endpoints
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
from typing import Dict, Any

from .observability import ObservabilityManager


class AndroidWorldHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AndroidWorld worker endpoints"""

    def __init__(self, *args, observability_manager=None, **kwargs):
        self.observability_manager = observability_manager
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            if path == "/health":
                self._handle_health()
            elif path == "/ready":
                self._handle_ready()
            elif path == "/metrics":
                self._handle_metrics()
            elif path == "/status":
                self._handle_status()
            elif path == "/trace":
                self._handle_trace()
            else:
                self._handle_not_found()

        except Exception as e:
            self._handle_error(e)

    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            if path == "/task":
                self._handle_task()
            else:
                self._handle_not_found()

        except Exception as e:
            self._handle_error(e)

    def _handle_health(self):
        """Health check endpoint"""
        if self.observability_manager:
            status = self.observability_manager.get_health_status()
        else:
            status = {
                "status": "healthy",
                "timestamp": time.time(),
                "service": "androidworld-worker",
            }

        self._send_json_response(status, 200)

    def _handle_ready(self):
        """Readiness probe endpoint"""
        # Check if the service is ready to handle requests
        ready = self._check_readiness()

        if ready:
            self._send_json_response({"status": "ready"}, 200)
        else:
            self._send_json_response({"status": "not_ready"}, 503)

    def _handle_metrics(self):
        """Metrics endpoint for Prometheus scraping"""
        metrics = self._collect_metrics()
        self._send_text_response(metrics, 200, "text/plain")

    def _handle_status(self):
        """Status endpoint with detailed service information"""
        status = {
            "service": "androidworld-worker",
            "version": "1.0.0",
            "uptime": time.time() - self.server.start_time,
            "environment": os.getenv("ENVIRONMENT", "production"),
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", "unknown"),
            "timestamp": time.time(),
        }

        self._send_json_response(status, 200)

    def _handle_trace(self):
        """Trace information endpoint"""
        if self.observability_manager:
            trace_info = {
                "trace_id": self.observability_manager.trace_id,
                "span_id": self.observability_manager.span_id,
                "service": "androidworld-worker",
            }
        else:
            trace_info = {
                "trace_id": None,
                "span_id": None,
                "service": "androidworld-worker",
            }

        self._send_json_response(trace_info, 200)

    def _handle_task(self):
        """Task execution endpoint"""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            task_data = json.loads(post_data.decode("utf-8"))

            # Log task start
            if self.observability_manager:
                self.observability_manager.log_task_start(
                    task_data.get("task_id", "unknown"),
                    task_data.get("task_type", "unknown"),
                    task_data,
                )

            # Simulate task execution
            result = self._execute_task(task_data)

            # Log task completion
            if self.observability_manager:
                self.observability_manager.log_task_completion(
                    task_data.get("task_id", "unknown"),
                    task_data.get("task_type", "unknown"),
                    result,
                    result.get("duration", 0),
                    result.get("success", False),
                )

            self._send_json_response(result, 200)

        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self._send_json_response({"error": str(e)}, 500)

    def _handle_not_found(self):
        """Handle 404 errors"""
        self._send_json_response({"error": "Not found"}, 404)

    def _handle_error(self, error):
        """Handle internal errors"""
        if self.observability_manager:
            self.observability_manager.log_error(error, {"endpoint": self.path})

        self._send_json_response({"error": str(error)}, 500)

    def _check_readiness(self) -> bool:
        """Check if the service is ready"""
        # Add your readiness checks here
        # For example, check if ADB is available, Genymotion is connected, etc.
        return True

    def _collect_metrics(self) -> str:
        """Collect Prometheus-style metrics"""
        metrics = []

        # Add your custom metrics here
        metrics.append(
            "# HELP androidworld_tasks_total Total number of tasks processed"
        )
        metrics.append("# TYPE androidworld_tasks_total counter")
        metrics.append('androidworld_tasks_total{service="androidworld-worker"} 0')

        metrics.append(
            "# HELP androidworld_task_duration_seconds Task execution duration"
        )
        metrics.append("# TYPE androidworld_task_duration_seconds histogram")
        metrics.append(
            'androidworld_task_duration_seconds{service="androidworld-worker"} 0'
        )

        return "\n".join(metrics)

    def _execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task (placeholder implementation)"""
        start_time = time.time()

        # Simulate task execution
        time.sleep(0.1)

        duration = time.time() - start_time

        return {
            "task_id": task_data.get("task_id"),
            "task_type": task_data.get("task_type"),
            "success": True,
            "duration": duration,
            "result": "Task completed successfully",
            "timestamp": time.time(),
        }

    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode("utf-8"))

    def _send_text_response(
        self, data: str, status_code: int = 200, content_type: str = "text/plain"
    ):
        """Send text response"""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(data.encode("utf-8"))

    def log_message(self, format, *args):
        """Override to use our observability manager for logging"""
        if self.observability_manager:
            self.observability_manager.logger.info(
                f"{self.address_string()} - {format % args}"
            )
        else:
            super().log_message(format, *args)


class AndroidWorldServer:
    """AndroidWorld worker web server"""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        observability_manager: ObservabilityManager = None,
    ):
        self.host = host
        self.port = port
        self.observability_manager = observability_manager
        self.server = None
        self.start_time = time.time()

    def start(self):
        """Start the web server"""

        def handler_factory(*args, **kwargs):
            return AndroidWorldHandler(
                *args, observability_manager=self.observability_manager, **kwargs
            )

        self.server = HTTPServer((self.host, self.port), handler_factory)
        self.server.start_time = self.start_time

        print(f"Starting AndroidWorld server on {self.host}:{self.port}")

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server...")
            self.stop()

    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("Server stopped")


def main():
    """Main function to run the web server"""
    import argparse

    parser = argparse.ArgumentParser(description="AndroidWorld Worker Web Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument(
        "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT", "unknown"),
        help="Google Cloud Project ID",
    )

    args = parser.parse_args()

    # Initialize observability manager
    observability_manager = ObservabilityManager(args.project_id)

    # Create and start server
    server = AndroidWorldServer(args.host, args.port, observability_manager)
    server.start()


if __name__ == "__main__":
    main()
