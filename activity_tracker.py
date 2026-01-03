"""
Activity Tracker for Discord Bot
Tracks bot activity and detects periods of inactivity
"""
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ActivityTracker:
    """Tracks Discord bot activity and monitors for inactivity"""

    def __init__(self, activity_file: str = './logs/bot_activity.json'):
        """
        Initialize the activity tracker

        Args:
            activity_file: Path to file where activity data is stored
        """
        self.activity_file = Path(activity_file)
        self.last_activity_time = None
        self.total_messages_processed = 0
        self.bot_start_time = None

        # Configure logging
        self.logger = logging.getLogger('activity_tracker')
        self.logger.setLevel(logging.INFO)

        # Create handler for console if not exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Ensure directory exists
        self.activity_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing activity data
        self._load_activity_data()

    def _load_activity_data(self):
        """Load activity data from file"""
        try:
            if self.activity_file.exists():
                with open(self.activity_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Parse timestamps
                if data.get('last_activity_time'):
                    self.last_activity_time = datetime.fromisoformat(data['last_activity_time'])

                if data.get('bot_start_time'):
                    self.bot_start_time = datetime.fromisoformat(data['bot_start_time'])

                self.total_messages_processed = data.get('total_messages_processed', 0)

                self.logger.info(f"📊 Activity data loaded from {self.activity_file}")
                if self.last_activity_time:
                    self.logger.info(f"   Last activity: {self.last_activity_time.isoformat()}")

        except Exception as e:
            self.logger.warning(f"⚠️ Could not load activity data: {e}")
            self.logger.info("   Starting with fresh activity tracking")

    def _save_activity_data(self):
        """Save activity data to file"""
        try:
            data = {
                'last_activity_time': self.last_activity_time.isoformat() if self.last_activity_time else None,
                'bot_start_time': self.bot_start_time.isoformat() if self.bot_start_time else None,
                'total_messages_processed': self.total_messages_processed,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.activity_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"❌ Error saving activity data: {e}")

    async def record_activity(self):
        """
        Record bot activity (message processed)
        Should be called every time the bot processes a message
        """
        self.last_activity_time = datetime.now()
        self.total_messages_processed += 1

        # Save to file asynchronously
        await asyncio.to_thread(self._save_activity_data)

        # Log activity every 100 messages
        if self.total_messages_processed % 100 == 0:
            self.logger.info(f"📊 Activity recorded: {self.total_messages_processed} total messages processed")

    def record_bot_start(self):
        """Record when the bot starts"""
        self.bot_start_time = datetime.now()
        self.last_activity_time = datetime.now()
        self._save_activity_data()

        self.logger.info(f"🚀 Bot start recorded at {self.bot_start_time.isoformat()}")

    def get_time_since_last_activity(self) -> Optional[timedelta]:
        """
        Get time elapsed since last activity

        Returns:
            timedelta object with time since last activity, or None if no activity recorded
        """
        if not self.last_activity_time:
            return None

        return datetime.now() - self.last_activity_time

    def get_hours_since_last_activity(self) -> Optional[float]:
        """
        Get hours elapsed since last activity

        Returns:
            Hours since last activity as float, or None if no activity recorded
        """
        time_delta = self.get_time_since_last_activity()

        if time_delta is None:
            return None

        return time_delta.total_seconds() / 3600

    def is_inactive(self, threshold_hours: float = 8.0) -> bool:
        """
        Check if bot has been inactive for longer than threshold

        Args:
            threshold_hours: Inactivity threshold in hours (default: 8.0)

        Returns:
            True if bot has been inactive longer than threshold, False otherwise
        """
        hours_inactive = self.get_hours_since_last_activity()

        if hours_inactive is None:
            # No activity recorded yet - consider inactive
            return True

        return hours_inactive >= threshold_hours

    def get_activity_status(self) -> dict:
        """
        Get comprehensive activity status

        Returns:
            Dictionary with activity status information
        """
        hours_inactive = self.get_hours_since_last_activity()

        status = {
            'last_activity_time': self.last_activity_time.isoformat() if self.last_activity_time else None,
            'bot_start_time': self.bot_start_time.isoformat() if self.bot_start_time else None,
            'total_messages_processed': self.total_messages_processed,
            'hours_since_last_activity': hours_inactive,
            'is_inactive_8h': self.is_inactive(8.0),
            'is_inactive_24h': self.is_inactive(24.0),
            'current_time': datetime.now().isoformat()
        }

        if self.bot_start_time:
            uptime = datetime.now() - self.bot_start_time
            status['uptime_hours'] = uptime.total_seconds() / 3600

        return status

    def print_status(self):
        """Print activity status to console"""
        status = self.get_activity_status()

        print("\n" + "=" * 60)
        print("📊 DISCORD BOT ACTIVITY STATUS")
        print("=" * 60)

        if status['last_activity_time']:
            print(f"Last Activity:     {status['last_activity_time']}")
        else:
            print(f"Last Activity:     No activity recorded")

        if status['bot_start_time']:
            print(f"Bot Started:       {status['bot_start_time']}")

        print(f"Messages Processed: {status['total_messages_processed']}")

        if status['hours_since_last_activity'] is not None:
            hours = status['hours_since_last_activity']
            print(f"Time Since Activity: {hours:.2f} hours ({hours*60:.1f} minutes)")

            if hours >= 8:
                print(f"Status:            🔴 INACTIVE (>{hours:.1f}h)")
            elif hours >= 4:
                print(f"Status:            🟡 WARNING ({hours:.1f}h)")
            else:
                print(f"Status:            🟢 ACTIVE ({hours:.1f}h)")
        else:
            print(f"Status:            🔴 NO ACTIVITY RECORDED")

        if status.get('uptime_hours'):
            print(f"Bot Uptime:        {status['uptime_hours']:.2f} hours")

        print("=" * 60 + "\n")


# Test function
def test_activity_tracker():
    """Test the activity tracker"""
    import asyncio

    async def run_test():
        tracker = ActivityTracker('./logs/test_activity.json')

        print("🧪 Testing Activity Tracker...")

        # Record bot start
        tracker.record_bot_start()

        # Simulate some activity
        print("\n📝 Simulating 5 messages...")
        for i in range(5):
            await tracker.record_activity()
            await asyncio.sleep(0.5)

        # Check status
        tracker.print_status()

        # Test inactivity check
        print(f"Is inactive (8h)?: {tracker.is_inactive(8.0)}")
        print(f"Is inactive (0.001h)?: {tracker.is_inactive(0.001)}")

        # Get full status
        status = tracker.get_activity_status()
        print(f"\n📊 Full status: {json.dumps(status, indent=2)}")

        print("\n✅ Activity tracker test completed")

    asyncio.run(run_test())


if __name__ == "__main__":
    test_activity_tracker()
