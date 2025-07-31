"""API monitoring and alerting for DEGIRO integration."""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
import threading
from enum import Enum

from core.logging_config import get_logger
from core.exceptions import DEGIROError, RateLimitError, SessionExpiredError


logger = get_logger("api_monitor")


class MetricType(Enum):
    """Types of metrics to track."""
    REQUEST_COUNT = "request_count"
    ERROR_COUNT = "error_count"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    RATE_LIMIT_HIT = "rate_limit_hit"
    SESSION_DURATION = "session_duration"
    RECONNECT_COUNT = "reconnect_count"


@dataclass
class APIMetric:
    """Container for API metrics."""
    timestamp: datetime
    metric_type: MetricType
    value: float
    endpoint: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert configuration."""
    name: str
    condition: Callable[[List[APIMetric]], bool]
    message: str
    severity: str = "warning"  # info, warning, error, critical
    cooldown: int = 300  # Seconds before alert can fire again
    last_fired: Optional[datetime] = None


class APIMonitor:
    """Monitor API performance and health."""
    
    def __init__(self, 
                 window_size: int = 300,  # 5 minutes
                 alert_callbacks: Optional[Dict[str, Callable]] = None):
        self.window_size = window_size
        self.metrics: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Alert] = []
        self.alert_callbacks = alert_callbacks or {}
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None
        
        # Initialize default alerts
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default monitoring alerts."""
        
        # High error rate alert
        self.add_alert(Alert(
            name="high_error_rate",
            condition=lambda metrics: self._calculate_error_rate(metrics) > 0.1,
            message="High error rate detected: {error_rate:.1%}",
            severity="error"
        ))
        
        # Rate limit alert
        self.add_alert(Alert(
            name="rate_limit_exceeded",
            condition=lambda metrics: self._count_rate_limits(metrics) > 5,
            message="Rate limit hit {count} times in last 5 minutes",
            severity="warning"
        ))
        
        # Slow response time alert
        self.add_alert(Alert(
            name="slow_response",
            condition=lambda metrics: self._average_response_time(metrics) > 5000,
            message="Average response time {avg_time}ms exceeds threshold",
            severity="warning"
        ))
        
        # Session instability alert
        self.add_alert(Alert(
            name="session_instability",
            condition=lambda metrics: self._count_reconnects(metrics) > 3,
            message="Session reconnected {count} times in last 5 minutes",
            severity="error"
        ))
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="APIMonitor"
            )
            self._monitor_thread.start()
            logger.info("API monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("API monitoring stopped")
    
    def record_metric(self, metric: APIMetric):
        """Record a new metric."""
        with self._lock:
            self.metrics[metric.metric_type].append(metric)
    
    def record_request(self, endpoint: str, response_time: float, success: bool, error: Optional[Exception] = None):
        """Record API request metrics."""
        timestamp = datetime.now()
        
        # Record request count
        self.record_metric(APIMetric(
            timestamp=timestamp,
            metric_type=MetricType.REQUEST_COUNT,
            value=1,
            endpoint=endpoint
        ))
        
        # Record response time
        self.record_metric(APIMetric(
            timestamp=timestamp,
            metric_type=MetricType.RESPONSE_TIME,
            value=response_time,
            endpoint=endpoint
        ))
        
        # Record error if occurred
        if not success:
            error_details = {
                "error_type": type(error).__name__ if error else "Unknown",
                "error_message": str(error) if error else ""
            }
            
            self.record_metric(APIMetric(
                timestamp=timestamp,
                metric_type=MetricType.ERROR_COUNT,
                value=1,
                endpoint=endpoint,
                details=error_details
            ))
            
            # Check for specific error types
            if isinstance(error, RateLimitError):
                self.record_metric(APIMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.RATE_LIMIT_HIT,
                    value=1,
                    endpoint=endpoint
                ))
    
    def record_session_event(self, event_type: str, details: Optional[Dict] = None):
        """Record session-related events."""
        timestamp = datetime.now()
        
        if event_type == "reconnect":
            self.record_metric(APIMetric(
                timestamp=timestamp,
                metric_type=MetricType.RECONNECT_COUNT,
                value=1,
                details=details or {}
            ))
        elif event_type == "session_duration":
            self.record_metric(APIMetric(
                timestamp=timestamp,
                metric_type=MetricType.SESSION_DURATION,
                value=details.get("duration_seconds", 0) if details else 0,
                details=details or {}
            ))
    
    def add_alert(self, alert: Alert):
        """Add a monitoring alert."""
        self.alerts.append(alert)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                self._check_alerts()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(10)  # Check every 10 seconds
    
    def _check_alerts(self):
        """Check all alerts against current metrics."""
        with self._lock:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(seconds=self.window_size)
            
            # Get recent metrics
            recent_metrics = []
            for metric_type, metrics in self.metrics.items():
                recent_metrics.extend([
                    m for m in metrics 
                    if m.timestamp > cutoff_time
                ])
            
            # Check each alert
            for alert in self.alerts:
                # Check cooldown
                if alert.last_fired:
                    if (current_time - alert.last_fired).total_seconds() < alert.cooldown:
                        continue
                
                # Check condition
                try:
                    if alert.condition(recent_metrics):
                        self._fire_alert(alert, recent_metrics)
                        alert.last_fired = current_time
                except Exception as e:
                    logger.error(f"Error checking alert {alert.name}: {e}")
    
    def _fire_alert(self, alert: Alert, metrics: List[APIMetric]):
        """Fire an alert."""
        # Prepare context for message formatting
        context = {
            "error_rate": self._calculate_error_rate(metrics),
            "count": len(metrics),
            "avg_time": self._average_response_time(metrics)
        }
        
        message = alert.message.format(**context)
        
        # Log alert
        if alert.severity == "critical":
            logger.critical(f"ALERT [{alert.name}]: {message}")
        elif alert.severity == "error":
            logger.error(f"ALERT [{alert.name}]: {message}")
        elif alert.severity == "warning":
            logger.warning(f"ALERT [{alert.name}]: {message}")
        else:
            logger.info(f"ALERT [{alert.name}]: {message}")
        
        # Call alert callbacks
        if alert.severity in self.alert_callbacks:
            try:
                self.alert_callbacks[alert.severity](alert.name, message)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _calculate_error_rate(self, metrics: List[APIMetric]) -> float:
        """Calculate error rate from metrics."""
        requests = sum(1 for m in metrics if m.metric_type == MetricType.REQUEST_COUNT)
        errors = sum(1 for m in metrics if m.metric_type == MetricType.ERROR_COUNT)
        
        return errors / requests if requests > 0 else 0
    
    def _count_rate_limits(self, metrics: List[APIMetric]) -> int:
        """Count rate limit hits."""
        return sum(1 for m in metrics if m.metric_type == MetricType.RATE_LIMIT_HIT)
    
    def _average_response_time(self, metrics: List[APIMetric]) -> float:
        """Calculate average response time."""
        response_times = [m.value for m in metrics if m.metric_type == MetricType.RESPONSE_TIME]
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _count_reconnects(self, metrics: List[APIMetric]) -> int:
        """Count reconnection events."""
        return sum(1 for m in metrics if m.metric_type == MetricType.RECONNECT_COUNT)
    
    def get_statistics(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get monitoring statistics."""
        with self._lock:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(minutes=window_minutes)
            
            stats = {
                "window_minutes": window_minutes,
                "timestamp": current_time.isoformat(),
                "metrics": {}
            }
            
            # Calculate stats for each metric type
            for metric_type, metrics in self.metrics.items():
                recent = [m for m in metrics if m.timestamp > cutoff_time]
                
                if recent:
                    if metric_type in [MetricType.REQUEST_COUNT, MetricType.ERROR_COUNT]:
                        stats["metrics"][metric_type.value] = len(recent)
                    elif metric_type == MetricType.RESPONSE_TIME:
                        values = [m.value for m in recent]
                        stats["metrics"][metric_type.value] = {
                            "avg": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "count": len(values)
                        }
                    else:
                        stats["metrics"][metric_type.value] = sum(m.value for m in recent)
            
            # Calculate derived metrics
            if MetricType.REQUEST_COUNT.value in stats["metrics"] and MetricType.ERROR_COUNT.value in stats["metrics"]:
                total_requests = stats["metrics"][MetricType.REQUEST_COUNT.value]
                total_errors = stats["metrics"][MetricType.ERROR_COUNT.value]
                stats["metrics"]["success_rate"] = (total_requests - total_errors) / total_requests if total_requests > 0 else 1.0
                stats["metrics"]["error_rate"] = total_errors / total_requests if total_requests > 0 else 0.0
            
            return stats
    
    def export_metrics(self, filepath: str, format: str = "json"):
        """Export metrics to file."""
        stats = self.get_statistics(window_minutes=1440)  # Last 24 hours
        
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Metrics exported to {filepath}")


# Global monitor instance
api_monitor = APIMonitor()


# Decorator for monitoring API calls
def monitored_api_call(endpoint: str):
    """Decorator to monitor API calls."""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error = None
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error = e
                raise
            finally:
                response_time = (time.time() - start_time) * 1000  # milliseconds
                api_monitor.record_request(endpoint, response_time, success, error)
        
        return wrapper
    return decorator