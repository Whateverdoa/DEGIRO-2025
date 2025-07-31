"""Human-like behavior patterns for API interactions."""

import random
import time
from datetime import datetime, time as datetime_time
from typing import Tuple
from core.logging_config import get_logger


logger = get_logger("human_behavior")


class HumanBehavior:
    """Simulate human-like interaction patterns."""
    
    @staticmethod
    def random_delay(min_seconds: float = 0.5, max_seconds: float = 3.0) -> float:
        """
        Generate a random delay to simulate human thinking/typing time.
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
            
        Returns:
            Actual delay time used
        """
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Human-like delay: {delay:.2f}s")
        time.sleep(delay)
        return delay
    
    @staticmethod
    def typing_delay(text_length: int) -> float:
        """
        Simulate typing delay based on text length.
        Average typing speed: 40-60 words per minute
        """
        # Assume average 5 characters per word
        words = text_length / 5
        # 40-60 WPM = 0.67-1 words per second
        typing_speed = random.uniform(0.67, 1.0)
        delay = words / typing_speed
        
        # Add some randomness
        delay *= random.uniform(0.8, 1.2)
        
        logger.debug(f"Typing delay for {text_length} chars: {delay:.2f}s")
        time.sleep(delay)
        return delay
    
    @staticmethod
    def mouse_movement_delay() -> float:
        """Simulate time to move mouse and click."""
        delay = random.uniform(0.3, 1.2)
        logger.debug(f"Mouse movement delay: {delay:.2f}s")
        time.sleep(delay)
        return delay
    
    @staticmethod
    def is_trading_hours() -> bool:
        """Check if current time is within typical trading hours."""
        now = datetime.now()
        current_time = now.time()
        
        # European trading hours (9:00 - 17:30 CET)
        # Adjust for your timezone
        market_open = datetime_time(9, 0)
        market_close = datetime_time(17, 30)
        
        # Also consider weekdays only
        is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6
        
        return is_weekday and market_open <= current_time <= market_close
    
    @staticmethod
    def get_activity_pattern() -> str:
        """
        Determine activity pattern based on time of day.
        
        Returns:
            Activity level: 'high', 'medium', 'low'
        """
        now = datetime.now()
        hour = now.hour
        
        # Typical trading activity patterns
        if 9 <= hour <= 10 or 15 <= hour <= 16:
            return 'high'  # Market open/close
        elif 11 <= hour <= 14:
            return 'medium'  # Mid-day
        else:
            return 'low'  # Off-hours
    
    @staticmethod
    def get_request_interval() -> Tuple[float, float]:
        """
        Get appropriate request interval based on activity pattern.
        
        Returns:
            Tuple of (min_interval, max_interval) in seconds
        """
        pattern = HumanBehavior.get_activity_pattern()
        
        if pattern == 'high':
            return (30, 120)  # 0.5-2 minutes
        elif pattern == 'medium':
            return (120, 300)  # 2-5 minutes
        else:
            return (300, 600)  # 5-10 minutes
    
    @staticmethod
    def add_request_jitter(base_interval: float) -> float:
        """Add random jitter to request intervals."""
        jitter = random.uniform(-0.2, 0.2) * base_interval
        return max(1, base_interval + jitter)
    
    @staticmethod
    def simulate_reading_time(text_length: int) -> float:
        """
        Simulate time needed to read text.
        Average reading speed: 200-250 words per minute
        """
        words = text_length / 5  # Assume 5 chars per word
        reading_speed = random.uniform(200, 250) / 60  # Words per second
        delay = words / reading_speed
        
        # Add some randomness
        delay *= random.uniform(0.8, 1.2)
        
        # Minimum reading time
        delay = max(delay, 0.5)
        
        logger.debug(f"Reading delay for {text_length} chars: {delay:.2f}s")
        time.sleep(delay)
        return delay
    
    @staticmethod
    def should_check_portfolio() -> bool:
        """
        Determine if it's appropriate to check portfolio.
        Humans don't constantly check their portfolio.
        """
        if not HumanBehavior.is_trading_hours():
            # Lower chance outside trading hours
            return random.random() < 0.1  # 10% chance
        
        pattern = HumanBehavior.get_activity_pattern()
        chances = {
            'high': 0.4,    # 40% chance during high activity
            'medium': 0.25,  # 25% chance during medium activity
            'low': 0.1      # 10% chance during low activity
        }
        
        return random.random() < chances.get(pattern, 0.1)
    
    @staticmethod
    def get_session_duration() -> int:
        """
        Get a human-like session duration in minutes.
        Most people don't stay logged in for hours.
        """
        # Typical session: 5-45 minutes
        if HumanBehavior.is_trading_hours():
            return random.randint(10, 45)
        else:
            return random.randint(5, 20)
    
    @staticmethod
    def add_user_agent_rotation() -> str:
        """Get a random user agent string."""
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        return random.choice(user_agents)


class HumanlikeDegiroSession:
    """Manage DEGIRO sessions with human-like behavior."""
    
    def __init__(self):
        self.last_action_time = None
        self.session_start = None
        self.action_count = 0
        
    def before_action(self, action_type: str = "general"):
        """Called before any API action."""
        if self.last_action_time:
            # Time since last action
            time_since = (datetime.now() - self.last_action_time).total_seconds()
            
            # If it's been too recent, add delay
            if time_since < 2:
                HumanBehavior.random_delay(2, 5)
        
        # Action-specific delays
        if action_type == "login":
            HumanBehavior.typing_delay(20)  # Username + password
        elif action_type == "search":
            HumanBehavior.typing_delay(10)  # Search term
        elif action_type == "order":
            HumanBehavior.random_delay(5, 10)  # Thinking time before order
        
        self.action_count += 1
        logger.debug(f"Action {self.action_count}: {action_type}")
    
    def after_action(self):
        """Called after any API action."""
        self.last_action_time = datetime.now()
        
        # Random chance to pause (human distraction)
        if random.random() < 0.1:  # 10% chance
            pause_time = random.uniform(10, 30)
            logger.debug(f"Human distraction pause: {pause_time:.1f}s")
            time.sleep(pause_time)
    
    def should_continue_session(self) -> bool:
        """Check if session should continue."""
        if not self.session_start:
            return True
            
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60
        max_duration = HumanBehavior.get_session_duration()
        
        if session_duration > max_duration:
            logger.info(f"Session duration ({session_duration:.1f}m) exceeded human-like limit ({max_duration}m)")
            return False
            
        # Also limit number of actions per session
        if self.action_count > 50:
            logger.info("Action count exceeded human-like limit")
            return False
            
        return True