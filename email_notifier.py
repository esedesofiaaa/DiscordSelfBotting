"""
Email Notification Service
Sends email alerts when the Discord bot experiences inactivity
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List


class EmailNotifier:
    """Email notification service for bot alerts"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_emails: List[str],
        use_tls: bool = True
    ):
        """
        Initialize the email notification service

        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP server port (e.g., 587 for TLS, 465 for SSL)
            sender_email: Email address to send from
            sender_password: Password or app-specific password for sender email
            recipient_emails: List of email addresses to send notifications to
            use_tls: Whether to use TLS encryption (default: True)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails
        self.use_tls = use_tls

        # Configure logging
        self.logger = logging.getLogger('email_notifier')
        self.logger.setLevel(logging.INFO)

        # Create handler for console if not exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Statistics
        self.emails_sent = 0
        self.emails_failed = 0
        self.last_email_time = None

    def send_notification(
        self,
        subject: str,
        message: str,
        is_html: bool = False
    ) -> bool:
        """
        Send email notification

        Args:
            subject: Email subject line
            message: Email message body
            is_html: Whether the message is HTML formatted (default: False)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Attach message body
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))

            # Connect to SMTP server and send email
            self.logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")

            if self.use_tls:
                # Use TLS (port 587 typically)
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
            else:
                # Use SSL (port 465 typically)
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)

            # Login and send
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()

            # Update statistics
            self.emails_sent += 1
            self.last_email_time = datetime.now()

            self.logger.info(f"✅ Email sent successfully to {len(self.recipient_emails)} recipient(s)")
            self.logger.info(f"   Subject: {subject}")

            return True

        except smtplib.SMTPAuthenticationError:
            self.emails_failed += 1
            self.logger.error("❌ SMTP Authentication failed - check email and password")
            return False

        except smtplib.SMTPConnectError:
            self.emails_failed += 1
            self.logger.error(f"❌ Failed to connect to SMTP server {self.smtp_server}:{self.smtp_port}")
            return False

        except Exception as e:
            self.emails_failed += 1
            self.logger.error(f"❌ Error sending email: {e}")
            return False

    def send_inactivity_alert(
        self,
        hours_inactive: float,
        last_activity_time: Optional[datetime] = None
    ) -> bool:
        """
        Send inactivity alert email

        Args:
            hours_inactive: Number of hours the bot has been inactive
            last_activity_time: Timestamp of last activity (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"⚠️ Discord Bot Inactivity Alert - {hours_inactive:.1f} hours"

        # Format last activity time
        if last_activity_time:
            last_activity_str = last_activity_time.strftime('%Y-%m-%d %H:%M:%S UTC')
        else:
            last_activity_str = "Unknown"

        # Create HTML message
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #ff6b6b; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                    <h1 style="margin: 0;">⚠️ Bot Inactivity Alert</h1>
                </div>

                <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
                    <h2 style="color: #dc3545; margin-top: 0;">Discord Bot Has Been Inactive</h2>

                    <p style="font-size: 16px; line-height: 1.6;">
                        Your Discord self-bot has not processed or received any messages for
                        <strong>{hours_inactive:.1f} hours</strong>.
                    </p>

                    <div style="background-color: white; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Last Activity:</strong> {last_activity_str}</p>
                        <p style="margin: 5px 0;"><strong>Alert Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p style="margin: 5px 0;"><strong>Inactive Duration:</strong> {hours_inactive:.1f} hours</p>
                    </div>

                    <h3 style="color: #495057;">Possible Issues:</h3>
                    <ul style="line-height: 1.8;">
                        <li>Bot process may have crashed or stopped</li>
                        <li>Discord connection may be interrupted</li>
                        <li>No messages in monitored channels</li>
                        <li>Network connectivity issues</li>
                        <li>Discord token may have expired</li>
                    </ul>

                    <h3 style="color: #495057;">Recommended Actions:</h3>
                    <ol style="line-height: 1.8;">
                        <li>Check if the bot process is running</li>
                        <li>Review bot logs for errors</li>
                        <li>Verify Discord connection status</li>
                        <li>Restart the bot if necessary</li>
                        <li>Check Discord token validity</li>
                    </ol>
                </div>

                <div style="background-color: #343a40; color: white; padding: 15px; border-radius: 0 0 5px 5px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">
                        This is an automated alert from your Discord Bot Monitoring System
                    </p>
                </div>
            </body>
        </html>
        """

        # Create plain text version
        plain_message = f"""
⚠️ DISCORD BOT INACTIVITY ALERT ⚠️

Your Discord self-bot has not processed or received any messages for {hours_inactive:.1f} hours.

DETAILS:
- Last Activity: {last_activity_str}
- Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- Inactive Duration: {hours_inactive:.1f} hours

POSSIBLE ISSUES:
- Bot process may have crashed or stopped
- Discord connection may be interrupted
- No messages in monitored channels
- Network connectivity issues
- Discord token may have expired

RECOMMENDED ACTIONS:
1. Check if the bot process is running
2. Review bot logs for errors
3. Verify Discord connection status
4. Restart the bot if necessary
5. Check Discord token validity

---
This is an automated alert from your Discord Bot Monitoring System
        """

        # Send HTML email with plain text fallback
        return self.send_notification(subject, html_message, is_html=True)

    def send_recovery_notification(self) -> bool:
        """
        Send notification that bot has recovered and is processing messages again

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "✅ Discord Bot Activity Resumed"

        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #51cf66; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                    <h1 style="margin: 0;">✅ Bot Activity Resumed</h1>
                </div>

                <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
                    <h2 style="color: #28a745; margin-top: 0;">Discord Bot is Active Again</h2>

                    <p style="font-size: 16px; line-height: 1.6;">
                        Your Discord self-bot has resumed processing messages and is now operating normally.
                    </p>

                    <div style="background-color: white; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Recovery Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p style="margin: 5px 0;"><strong>Status:</strong> Active and processing messages</p>
                    </div>
                </div>

                <div style="background-color: #343a40; color: white; padding: 15px; border-radius: 0 0 5px 5px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">
                        This is an automated notification from your Discord Bot Monitoring System
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_notification(subject, html_message, is_html=True)

    def test_connection(self) -> bool:
        """
        Test email configuration by sending a test email

        Returns:
            True if test email sent successfully, False otherwise
        """
        subject = "🧪 Discord Bot Email Notification Test"
        message = f"""
This is a test email from your Discord Bot Monitoring System.

Configuration:
- SMTP Server: {self.smtp_server}:{self.smtp_port}
- Sender: {self.sender_email}
- Recipients: {', '.join(self.recipient_emails)}
- Encryption: {'TLS' if self.use_tls else 'SSL'}

If you received this email, your email notification system is configured correctly!

Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """

        return self.send_notification(subject, message)

    def get_stats(self) -> dict:
        """Get email notification statistics"""
        return {
            "emails_sent": self.emails_sent,
            "emails_failed": self.emails_failed,
            "last_email_time": self.last_email_time.isoformat() if self.last_email_time else None,
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "sender_email": self.sender_email,
            "recipient_count": len(self.recipient_emails)
        }


# Test function
def test_email_notifier():
    """Test the email notification system"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get configuration from environment
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SMTP_SENDER_EMAIL', '')
    sender_password = os.getenv('SMTP_SENDER_PASSWORD', '')
    recipient_emails = os.getenv('ALERT_RECIPIENT_EMAILS', '').split(',')

    if not sender_email or not sender_password or not recipient_emails[0]:
        print("❌ Email configuration missing in .env file")
        print("   Required: SMTP_SERVER, SMTP_PORT, SMTP_SENDER_EMAIL, SMTP_SENDER_PASSWORD, ALERT_RECIPIENT_EMAILS")
        return False

    # Create notifier
    notifier = EmailNotifier(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        recipient_emails=[email.strip() for email in recipient_emails if email.strip()],
        use_tls=True
    )

    print("🧪 Testing email notification system...")

    # Test connection
    if notifier.test_connection():
        print("✅ Test email sent successfully!")
        print(f"📊 Stats: {notifier.get_stats()}")
        return True
    else:
        print("❌ Failed to send test email")
        return False


if __name__ == "__main__":
    test_email_notifier()
