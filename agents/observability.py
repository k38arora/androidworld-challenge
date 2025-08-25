"""
Observability and Tracing Integration for AndroidWorld Challenge
Integrates with Google Cloud Logging, Cloud Trace, and Cloud Monitoring
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

try:
    from google.cloud import logging_v2
    from google.cloud import trace_v1
    from google.cloud import monitoring_v3
    from google.cloud.monitoring_v3 import MetricDescriptor, TimeSeries
    from opentelemetry import trace
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print(
        "Warning: Google Cloud libraries not available. Observability features will be limited."
    )


class ObservabilityManager:
    """Manages observability, tracing, and monitoring for AndroidWorld tasks"""

    def __init__(self, project_id: str, service_name: str = "androidworld-worker"):
        self.project_id = project_id
        self.service_name = service_name
        self.trace_id = None
        self.span_id = None

        # Initialize Google Cloud clients if available
        if GOOGLE_CLOUD_AVAILABLE:
            self._setup_google_cloud()
        else:
            self._setup_fallback()

        # Initialize OpenTelemetry if available
        if GOOGLE_CLOUD_AVAILABLE:
            self._setup_opentelemetry()

    def _setup_google_cloud(self):
        """Initialize Google Cloud clients"""
        try:
            self.logging_client = logging_v2.LoggingServiceV2Client()
            self.trace_client = trace_v1.TraceServiceClient()
            self.monitoring_client = monitoring_v3.MetricServiceClient()

            # Set up structured logging
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)

        except Exception as e:
            print(f"Warning: Failed to initialize Google Cloud clients: {e}")
            self._setup_fallback()

    def _setup_fallback(self):
        """Setup fallback logging when Google Cloud is not available"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _setup_opentelemetry(self):
        """Initialize OpenTelemetry tracing"""
        try:
            # Create resource
            resource = Resource.create(
                {
                    "service.name": self.service_name,
                    "service.version": "1.0.0",
                    "cloud.provider": "gcp",
                    "cloud.project_id": self.project_id,
                }
            )

            # Create tracer provider
            provider = TracerProvider(resource=resource)

            # Create Cloud Trace exporter
            exporter = CloudTraceSpanExporter(project_id=self.project_id)

            # Add batch processor
            provider.add_span_processor(BatchSpanProcessor(exporter))

            # Set global tracer provider
            trace.set_tracer_provider(provider)

            # Get tracer
            self.tracer = trace.get_tracer(__name__)

            # Instrument HTTP libraries
            RequestsInstrumentor().instrument()
            URLLib3Instrumentor().instrument()

        except Exception as e:
            print(f"Warning: Failed to setup OpenTelemetry: {e}")

    @contextmanager
    def trace_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Context manager for tracing spans"""
        if not GOOGLE_CLOUD_AVAILABLE or not hasattr(self, "tracer"):
            # Fallback: just log the span
            start_time = time.time()
            try:
                yield
            finally:
                duration = time.time() - start_time
                self.logger.info(f"Span '{name}' completed in {duration:.3f}s")
            return

        # Create span with OpenTelemetry
        with self.tracer.start_as_current_span(
            name, attributes=attributes or {}
        ) as span:
            self.trace_id = span.get_span_context().trace_id
            self.span_id = span.get_span_context().span_id

            # Add custom attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))

            try:
                yield span
            except Exception as e:
                # Record error in span
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
            finally:
                # Record span duration
                span.set_attribute(
                    "duration_ms", (time.time() - span.start_time) * 1000
                )

    def log_task_start(self, task_id: str, task_type: str, task_data: Dict[str, Any]):
        """Log the start of a task execution"""
        log_entry = {
            "severity": "INFO",
            "message": f"Task started: {task_type}",
            "task_id": task_id,
            "task_type": task_type,
            "task_data": task_data,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "labels": {
                "service": self.service_name,
                "task_type": task_type,
                "environment": "production",
            },
        }

        self._write_log(log_entry)

    def log_task_completion(
        self,
        task_id: str,
        task_type: str,
        result: Dict[str, Any],
        duration: float,
        success: bool,
    ):
        """Log the completion of a task execution"""
        log_entry = {
            "severity": "INFO" if success else "ERROR",
            "message": f"Task completed: {task_type}",
            "task_id": task_id,
            "task_type": task_type,
            "result": result,
            "duration": duration,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "labels": {
                "service": self.service_name,
                "task_type": task_type,
                "environment": "production",
            },
        }

        self._write_log(log_entry)

        # Record custom metrics
        if GOOGLE_CLOUD_AVAILABLE:
            self._record_task_metrics(task_type, duration, success)

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log an error with context"""
        log_entry = {
            "severity": "ERROR",
            "message": str(error),
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "labels": {
                "service": self.service_name,
                "error_type": type(error).__name__,
                "environment": "production",
            },
        }

        self._write_log(log_entry)

    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to appropriate backend"""
        if GOOGLE_CLOUD_AVAILABLE and hasattr(self, "logging_client"):
            try:
                # Write to Google Cloud Logging
                log_name = f"projects/{self.project_id}/logs/{self.service_name}"

                # Convert to Google Cloud Logging format
                gcp_log_entry = logging_v2.LogEntry(
                    log_name=log_name,
                    severity=logging_v2.LogSeverity[log_entry["severity"]],
                    text_payload=json.dumps(log_entry),
                    timestamp=log_entry["timestamp"],
                    labels=log_entry["labels"],
                    trace=(
                        f"projects/{self.project_id}/traces/{self.trace_id}"
                        if self.trace_id
                        else None
                    ),
                    span_id=str(self.span_id) if self.span_id else None,
                )

                self.logging_client.write_log_entries([gcp_log_entry])

            except Exception as e:
                # Fallback to console logging
                self.logger.error(f"Failed to write to Google Cloud Logging: {e}")
                self.logger.info(json.dumps(log_entry))
        else:
            # Fallback to console logging
            self.logger.info(json.dumps(log_entry))

    def _record_task_metrics(self, task_type: str, duration: float, success: bool):
        """Record custom metrics for task execution"""
        try:
            # Create metric descriptor for task duration
            duration_metric = {
                "type": f"custom.googleapis.com/androidworld/task_duration",
                "display_name": f"AndroidWorld Task Duration - {task_type}",
                "description": f"Duration of {task_type} tasks in milliseconds",
                "metric_kind": "GAUGE",
                "value_type": "DOUBLE",
                "unit": "ms",
            }

            # Create time series for duration
            duration_series = TimeSeries(
                metric={
                    "type": duration_metric["type"],
                    "labels": {"task_type": task_type, "service": self.service_name},
                },
                resource={
                    "type": "gce_instance",
                    "labels": {
                        "project_id": self.project_id,
                        "instance_id": "androidworld-worker",
                    },
                },
                points=[
                    {
                        "interval": {"end_time": {"seconds": int(time.time())}},
                        "value": {
                            "double_value": duration * 1000  # Convert to milliseconds
                        },
                    }
                ],
            )

            # Create metric descriptor for task success rate
            success_metric = {
                "type": f"custom.googleapis.com/androidworld/task_success_rate",
                "display_name": f"AndroidWorld Task Success Rate - {task_type}",
                "description": f"Success rate of {task_type} tasks",
                "metric_kind": "GAUGE",
                "value_type": "DOUBLE",
                "unit": "1",
            }

            # Create time series for success rate
            success_value = 1.0 if success else 0.0
            success_series = TimeSeries(
                metric={
                    "type": success_metric["type"],
                    "labels": {"task_type": task_type, "service": self.service_name},
                },
                resource={
                    "type": "gce_instance",
                    "labels": {
                        "project_id": self.project_id,
                        "instance_id": "androidworld-worker",
                    },
                },
                points=[
                    {
                        "interval": {"end_time": {"seconds": int(time.time())}},
                        "value": {"double_value": success_value},
                    }
                ],
            )

            # Write metrics
            self.monitoring_client.create_time_series(
                request={
                    "name": f"projects/{self.project_id}",
                    "time_series": [duration_series, success_series],
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to record metrics: {e}")

    def generate_trace_report(self, task_id: str) -> Dict[str, Any]:
        """Generate a trace report for correlation with evaluation results"""
        return {
            "trace_id": str(self.trace_id) if self.trace_id else None,
            "span_id": str(self.span_id) if self.span_id else None,
            "task_id": task_id,
            "service_name": self.service_name,
            "project_id": self.project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_url": (
                f"https://console.cloud.google.com/traces/traces?project={self.project_id}&tid={self.trace_id}"
                if self.trace_id
                else None
            ),
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for health checks"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "project_id": self.project_id,
            "observability": {
                "google_cloud_available": GOOGLE_CLOUD_AVAILABLE,
                "opentelemetry_available": hasattr(self, "tracer"),
                "logging_available": hasattr(self, "logging_client"),
                "monitoring_available": hasattr(self, "monitoring_client"),
            },
        }
