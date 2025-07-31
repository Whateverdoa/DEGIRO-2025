"""Session management with automatic re-authentication and monitoring."""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from core.logging_config import get_logger
from core.config import settings
from core.human_behavior import HumanBehavior


logger = get_logger("session_manager")


class SessionManager:
    """Manages DEGIRO API sessions with auto-reconnection."""
    
    def __init__(self, 
                 check_interval: int = 60,
                 session_timeout: int = 25,  # Minutes, conservative estimate
                 max_reconnect_attempts: int = 5):
        self.check_interval = check_interval
        self.session_timeout = session_timeout
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        self._reconnect_callbacks = []
        self._disconnect_callbacks = []
        
        self.last_successful_check = None
        self.reconnect_count = 0
        self.total_reconnects = 0
        
        # Import here to avoid circular import
        from core.degiro_api import degiro_api
        self.degiro_api = degiro_api
        
    def add_reconnect_callback(self, callback: Callable):
        """Add callback to be called after successful reconnection."""
        self._reconnect_callbacks.append(callback)
        
    def add_disconnect_callback(self, callback: Callable):
        """Add callback to be called on disconnection."""
        self._disconnect_callbacks.append(callback)
    
    def start(self) -> bool:
        """
        Start session management and monitoring.
        
        Returns:
            True if initial connection successful
        """
        # Initial connection
        if not self.degiro_api.connect():
            logger.error("Failed to establish initial connection")
            return False
            
        # Start monitoring thread
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_session,
            daemon=True,
            name="SessionMonitor"
        )
        self._monitor_thread.start()
        
        logger.info("Session manager started successfully")
        return True
    
    def stop(self):
        """Stop session management and disconnect."""
        logger.info("Stopping session manager")
        
        # Stop monitoring
        self._stop_monitoring.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
            
        # Disconnect
        self.degiro_api.disconnect()
        
        # Call disconnect callbacks
        for callback in self._disconnect_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}")
    
    def _monitor_session(self):
        """Monitor session health and reconnect if needed."""
        logger.info("Session monitor started")
        
        while not self._stop_monitoring.is_set():
            try:
                # Check session health
                if self._should_check_session():
                    self._check_and_maintain_session()
                    
            except Exception as e:
                logger.error(f"Error in session monitor: {e}")
                
            # Wait for next check
            self._stop_monitoring.wait(self.check_interval)
            
        logger.info("Session monitor stopped")
    
    def _should_check_session(self) -> bool:
        """Determine if session check is needed."""
        if not self.degiro_api.last_activity_time:
            return True
            
        # Check if human session should continue
        if hasattr(self.degiro_api, 'human_session') and not self.degiro_api.human_session.should_continue_session():
            logger.info("Human-like session duration reached, disconnecting")
            self.degiro_api.disconnect()
            return False
            
        # Check if approaching timeout
        time_since_activity = datetime.now() - self.degiro_api.last_activity_time
        return time_since_activity.total_seconds() > (self.session_timeout * 60 * 0.8)  # 80% of timeout
    
    def _check_and_maintain_session(self):
        """Check session health and maintain connection."""
        try:
            # Perform health check
            health = self.degiro_api.health_check()
            
            if not health["connected"]:
                logger.warning("Session disconnected, attempting reconnection")
                self._handle_reconnection()
            else:
                # Perform a lightweight operation to keep session alive
                self._keep_alive()
                self.last_successful_check = datetime.now()
                self.reconnect_count = 0  # Reset on success
                
        except Exception as e:
            logger.error(f"Session check failed: {e}")
            self._handle_reconnection()
    
    def _keep_alive(self):
        """Perform lightweight operation to keep session alive."""
        try:
            # Get portfolio summary (lightweight operation)
            self.degiro_api.get_portfolio()
            logger.debug("Keep-alive successful")
        except Exception as e:
            logger.warning(f"Keep-alive failed: {e}")
            raise
    
    def _handle_reconnection(self):
        """Handle reconnection with backoff."""
        self.reconnect_count += 1
        
        if self.reconnect_count > self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) exceeded")
            # Call disconnect callbacks
            for callback in self._disconnect_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error in disconnect callback: {e}")
            return
            
        # Calculate backoff time
        backoff_time = min(300, 10 * (2 ** (self.reconnect_count - 1)))  # Max 5 minutes
        logger.info(f"Attempting reconnection {self.reconnect_count}/{self.max_reconnect_attempts} "
                   f"after {backoff_time}s backoff")
        
        time.sleep(backoff_time)
        
        try:
            # Disconnect first
            self.degiro_api.disconnect()
            
            # Reconnect
            if self.degiro_api.connect():
                self.total_reconnects += 1
                logger.info(f"Reconnection successful (total reconnects: {self.total_reconnects})")
                
                # Call reconnect callbacks
                for callback in self._reconnect_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Error in reconnect callback: {e}")
                        
                # Reset counter on success
                self.reconnect_count = 0
            else:
                logger.error("Reconnection failed")
                # Will retry on next monitor cycle
                
        except Exception as e:
            logger.error(f"Error during reconnection: {e}")
    
    def get_status(self) -> dict:
        """Get current session status."""
        return {
            "connected": self.degiro_api.is_connected,
            "last_successful_check": self.last_successful_check.isoformat() if self.last_successful_check else None,
            "reconnect_count": self.reconnect_count,
            "total_reconnects": self.total_reconnects,
            "monitor_running": self._monitor_thread and self._monitor_thread.is_alive(),
            "api_health": self.degiro_api.health_check()
        }
    
    def force_reconnect(self):
        """Force immediate reconnection."""
        logger.info("Forcing reconnection")
        self._handle_reconnection()


# Global session manager instance
session_manager = SessionManager()