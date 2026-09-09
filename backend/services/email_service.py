import os
import smtplib
import asyncio
import secrets
import time
from pathlib import Path
from email.utils import formatdate, make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL", self.username or "noreply@artha-analytics.com")
        self.logo_url = os.getenv("APP_LOGO_URL")

    def _send_sync(self, recipient_email: str, otp_code: str) -> None:
        if not self.smtp_host or not self.username or not self.password:
            logger.info(
                f"[EmailService - Local Dev] SMTP credentials missing. OTP for {recipient_email} is: [{otp_code}]"
            )
            return

        domain = self.sender_email.split("@")[-1] if "@" in self.sender_email else "artha-analytics.com"

        # Construct root multipart/related container
        msg = MIMEMultipart("related")
        msg["Subject"] = f"{otp_code} is your Artha Analytics Verification Code"
        msg["From"] = f"Artha Analytics <{self.sender_email}>"
        msg["To"] = recipient_email
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(idstring=secrets.token_hex(6), domain=domain)
        msg["X-Mailer"] = "ArthaAnalytics-Mailer/1.0"
        msg["Auto-Submitted"] = "auto-generated"

        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)

        # Plaintext fallback for strict text clients & anti-spam scoring
        text_body = (
            f"Artha Analytics Verification Code: {otp_code}\n\n"
            f"Please enter this 6-digit code to complete your account registration.\n"
            f"This code will expire in 5 minutes.\n\n"
            f"If you did not request this code, please ignore this email.\n\n"
            f"© Artha Analytics · Multi-Agent AI. Singular Market Edge."
        )
        msg_alternative.attach(MIMEText(text_body, "plain", "utf-8"))

        # Determine Logo HTML element (Hosted URL > HTML/CSS Brand Emblem matching AuthCard.tsx)
        if self.logo_url:
            logo_html = f'<img src="{self.logo_url}" alt="Artha Analytics" width="180" style="display: block; margin: 0 auto 20px auto; border: 0; outline: none; text-decoration: none;" />'
        else:
            logo_html = """
            <div style="text-align: center; margin-bottom: 24px;">
              <div style="font-size: 22px; font-weight: 700; color: #09090b; letter-spacing: -0.5px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">Artha Analytics</div>
              <div style="display: inline-flex; align-items: center; justify-content: center; gap: 6px; margin-top: 4px;">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #d4a84c; vertical-align: middle;"></span>
                <span style="font-size: 9.5px; font-weight: 700; color: #d4a84c; font-family: 'Courier New', Courier, monospace; letter-spacing: 1.8px; text-transform: uppercase; vertical-align: middle;">MULTI-AGENT AI. SINGULAR MARKET EDGE.</span>
              </div>
            </div>
            """

        # HTML body matching AuthCard design system
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f5; color: #09090b; margin: 0; padding: 30px 12px; -webkit-font-smoothing: antialiased; }}
            .container {{ max-width: 440px; margin: 0 auto; background: #ffffff; border: 1px solid #e4e4e7; border-radius: 16px; padding: 36px 28px; text-align: center; box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08); overflow: hidden; position: relative; }}
            .gold-bar {{ height: 4px; background: linear-gradient(90deg, #d4a84c, #f59e0b, #d4a84c); margin: -36px -28px 28px -28px; }}
            .title {{ font-size: 18px; font-weight: 700; color: #09090b; margin-bottom: 8px; letter-spacing: -0.02em; }}
            .desc {{ font-size: 13px; color: #71717a; line-height: 1.5; margin-bottom: 24px; max-width: 360px; margin-left: auto; margin-right: auto; }}
            .otp-container {{ background: #09090b; border: 1px solid #27272a; border-radius: 12px; padding: 18px 24px; display: inline-block; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
            .otp-code {{ font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 700; letter-spacing: 12px; color: #f59e0b; text-shadow: 0 0 10px rgba(245, 158, 11, 0.3); margin-left: 12px; }}
            .timer-badge {{ font-size: 12px; font-weight: 600; color: #d97706; background: #fef3c7; border: 1px solid #fde68a; border-radius: 20px; padding: 6px 16px; display: inline-block; margin-bottom: 24px; }}
            .footer {{ font-size: 11px; color: #a1a1aa; border-top: 1px solid #f4f4f5; padding-top: 20px; margin-top: 20px; line-height: 1.6; }}
            .tagline {{ font-size: 9px; font-family: monospace; color: #d4a84c; letter-spacing: 1.5px; margin-top: 6px; font-weight: 600; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="gold-bar"></div>
            {logo_html}
            <div class="title">Verify Your Email Address</div>
            <div class="desc">Please use the verification code below to complete your registration on Artha Analytics:</div>
            <div class="otp-container">
              <span class="otp-code">{otp_code}</span>
            </div>
            <br />
            <div class="timer-badge">⏱️ Code expires in <strong>5 minutes</strong></div>
            <div class="footer">
              <div>If you did not request this account registration, please ignore this email.</div>
              <div class="tagline">SECURED TRANSACTIONAL EMAIL · ARTHA ANALYTICS</div>
            </div>
          </div>
        </body>
        </html>
        """

        msg_alternative.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.sender_email, [recipient_email], msg.as_string())
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.sendmail(self.sender_email, [recipient_email], msg.as_string())
            logger.info(f"[EmailService] Sent OTP verification email to {recipient_email}")
        except Exception as e:
            logger.error(f"[EmailService] Failed to send email via SMTP: {e}. OTP was: [{otp_code}]")
            raise e

    async def send_otp_email(self, recipient_email: str, otp_code: str) -> None:
        await asyncio.to_thread(self._send_sync, recipient_email, otp_code)
