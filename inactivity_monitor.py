#!/usr/bin/env python3
"""
Inactivity Monitor for Discord Bot
Monitors bot activity and sends email alerts when inactive for extended periods
"""
import asyncio
import os
import signal
import logging
from datetime import datetime
from dotenv import load_dotenv
from activity_tracker import ActivityTracker
from email_notifier import EmailNotifier

# Load environment variables
load_dotenv()


class InactivityMonitor:
    """Monitor bot inactivity and send email alerts"""

    def __init__(
        self,
        inactivity_threshold_hours: float = 8.0,
        check_interval_minutes: float = 30.0
    ):
        """
        Initialize inactivity monitor

        Args:
            inactivity_threshold_hours: Hours of inactivity before sending alert (default: 8.0)
            check_interval_minutes: Minutes between inactivity checks (default: 30.0)
        """
        # Configuration
        self.inactivity_threshold_hours = inactivity_threshold_hours
        self.check_interval_seconds = check_interval_minutes * 60

        # Activity tracker
        activity_file = os.getenv('ACTIVITY_TRACKER_FILE', './logs/bot_activity.json')
        self.activity_tracker = ActivityTracker(activity_file)

        # Email notifier configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SMTP_SENDER_EMAIL', '')
        sender_password = os.getenv('SMTP_SENDER_PASSWORD', '')
        recipient_emails_str = os.getenv('ALERT_RECIPIENT_EMAILS', '')

        # Parse recipient emails
        recipient_emails = [email.strip() for email in recipient_emails_str.split(',') if email.strip()]

        # Create email notifier
        self.email_notifier = None
        if sender_email and sender_password and recipient_emails:
            self.email_notifier = EmailNotifier(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_emails=recipient_emails,
                use_tls=True
            )
            print(f"✅ Email notifications configured")
            print(f"   Recipients: {', '.join(recipient_emails)}")
        else:
            print("⚠️ Email notifications not configured - alerts will only be logged")

        # State tracking
        self.is_running = False
        self.alert_sent = False  # Track if alert has been sent
        self.last_check_time = None
        self.check_count = 0

        # Configure logging
        self.logger = logging.getLogger('inactivity_monitor')
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        print(f"🔍 Inactivity Monitor initialized")
        print(f"   Threshold: {self.inactivity_threshold_hours} hours")
        print(f"   Check interval: {check_interval_minutes} minutes")

    async def check_inactivity(self) -> bool:
        """
        Check for bot inactivity and send alert if necessary

        Returns:
            True if bot is inactive, False otherwise
        """
        self.last_check_time = datetime.now()
        self.check_count += 1

        # Get activity status
        status = self.activity_tracker.get_activity_status()
        hours_inactive = status.get('hours_since_last_activity')

        if hours_inactive is None:
            self.logger.warning("⚠️ No activity data available - bot may not have started yet")
            return False

        self.logger.info(f"🔍 Inactivity check #{self.check_count}: {hours_inactive:.2f}h since last activity")

        # Check if inactive beyond threshold
        if hours_inactive >= self.inactivity_threshold_hours:
            self.logger.warning(f"⚠️ Bot has been INACTIVE for {hours_inactive:.2f} hours (threshold: {self.inactivity_threshold_hours}h)")

            # Send alert if not already sent
            if not self.alert_sent:
                await self._send_inactivity_alert(hours_inactive, status.get('last_activity_time'))
                self.alert_sent = True
            else:
                self.logger.info("   Alert already sent for this inactivity period")

            return True
        else:
            # Bot is active - reset alert flag if it was previously set
            if self.alert_sent:
                self.logger.info(f"✅ Bot is active again after {hours_inactive:.2f}h")
                await self._send_recovery_notification()
                self.alert_sent = False

            self.logger.info(f"✅ Bot is active - {hours_inactive:.2f}h since last message")
            return False

    async def _send_inactivity_alert(self, hours_inactive: float, last_activity_time: str):
        """Send inactivity alert via email"""
        self.logger.warning(f"📧 Sending inactivity alert email...")

        if not self.email_notifier:
            self.logger.warning("⚠️ Email notifier not configured - cannot send alert")
            return

        try:
            # Parse last activity time
            last_activity_dt = None
            if last_activity_time:
                last_activity_dt = datetime.fromisoformat(last_activity_time)

            # Send email
            success = self.email_notifier.send_inactivity_alert(
                hours_inactive=hours_inactive,
                last_activity_time=last_activity_dt
            )

            if success:
                self.logger.info("✅ Inactivity alert email sent successfully")
            else:
                self.logger.error("❌ Failed to send inactivity alert email")

        except Exception as e:
            self.logger.error(f"❌ Error sending inactivity alert: {e}")

    async def _send_recovery_notification(self):
        """Send recovery notification via email"""
        self.logger.info(f"📧 Sending recovery notification email...")

        if not self.email_notifier:
            return

        try:
            success = self.email_notifier.send_recovery_notification()

            if success:
                self.logger.info("✅ Recovery notification email sent successfully")
            else:
                self.logger.error("❌ Failed to send recovery notification email")

        except Exception as e:
            self.logger.error(f"❌ Error sending recovery notification: {e}")

    async def monitor_loop(self):
        """Main monitoring loop"""
        self.is_running = True

        self.logger.info("🚀 Starting inactivity monitoring loop...")
        self.logger.info(f"   Checking every {self.check_interval_seconds/60:.1f} minutes")
        self.logger.info(f"   Alert threshold: {self.inactivity_threshold_hours} hours")

        # Initial check
        await self.check_inactivity()

        while self.is_running:
            try:
                # Wait for next check interval
                await asyncio.sleep(self.check_interval_seconds)

                if self.is_running:
                    # Perform inactivity check
                    await self.check_inactivity()

            except asyncio.CancelledError:
                self.logger.info("⏹️ Monitoring loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                # Continue monitoring despite errors
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def start(self):
        """Start the inactivity monitor"""
        self.logger.info("🔍 Starting Inactivity Monitor...")

        # Show current status before starting
        self.activity_tracker.print_status()

        # Start monitoring loop
        await self.monitor_loop()

    async def stop(self):
        """Stop the inactivity monitor"""
        self.is_running = False
        self.logger.info("⏹️ Inactivity Monitor stopped")

    def get_monitor_status(self) -> dict:
        """Get monitor status information"""
        return {
            'is_running': self.is_running,
            'inactivity_threshold_hours': self.inactivity_threshold_hours,
            'check_interval_minutes': self.check_interval_seconds / 60,
            'check_count': self.check_count,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'alert_sent': self.alert_sent,
            'email_configured': self.email_notifier is not None,
            'activity_status': self.activity_tracker.get_activity_status()
        }


async def main():
    """Main entry point"""
    # Get configuration from environment
    inactivity_threshold = float(os.getenv('INACTIVITY_THRESHOLD_HOURS', '8.0'))
    check_interval = float(os.getenv('INACTIVITY_CHECK_INTERVAL_MINUTES', '30.0'))

    # Create monitor
    monitor = InactivityMonitor(
        inactivity_threshold_hours=inactivity_threshold,
        check_interval_minutes=check_interval
    )

    # Handle signals for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n📡 Signal {signum} received, stopping monitor...")
        asyncio.create_task(monitor.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await monitor.start()
    except KeyboardInterrupt:
        await monitor.stop()


if __name__ == "__main__":
    print("=" * 70)
    print("🔍 DISCORD BOT INACTIVITY MONITOR")
    print("=" * 70)
    print()

    asyncio.run(main())
