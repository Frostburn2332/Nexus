import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import settings
from .provider import EmailProvider


class GmailEmailProvider(EmailProvider):
    """Sends transactional email via Gmail SMTP using STARTTLS on port 587.

    Requires a 16-character Google App Password (not your Gmail account password).
    Generate one at: https://myaccount.google.com/apppasswords
    """

    async def send_invitation(
        self,
        to_email: str,
        inviter_name: str,
        organization_name: str,
        invitation_link: str,
    ) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"You've been invited to join {organization_name} on Nexus"
        msg["From"] = settings.mail_from
        msg["To"] = to_email

        plain = (
            f"Hi,\n\n"
            f"{inviter_name} has invited you to join {organization_name} on Nexus.\n\n"
            f"Accept your invitation here:\n{invitation_link}\n\n"
            f"This link expires in 7 days.\n\n"
            f"— The Nexus Team"
        )

        html = f"""
<!DOCTYPE html>
<html>
  <body style="font-family: sans-serif; background: #f9fafb; margin: 0; padding: 0;">
    <div style="max-width: 480px; margin: 48px auto; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 40px;">
      <h1 style="font-size: 20px; font-weight: 700; color: #4f46e5; margin: 0 0 8px;">Nexus</h1>
      <h2 style="font-size: 16px; font-weight: 600; color: #111827; margin: 0 0 16px;">
        You've been invited to join <span style="color: #4f46e5;">{organization_name}</span>
      </h2>
      <p style="font-size: 14px; color: #6b7280; margin: 0 0 24px;">
        <strong style="color: #111827;">{inviter_name}</strong> has invited you to collaborate on Nexus.
      </p>
      <a href="{invitation_link}"
         style="display: inline-block; background: #4f46e5; color: #fff; text-decoration: none;
                font-size: 14px; font-weight: 600; padding: 12px 24px; border-radius: 8px;">
        Accept Invitation
      </a>
      <p style="font-size: 12px; color: #9ca3af; margin: 24px 0 0;">
        This link expires in 7 days. If you weren't expecting this, you can safely ignore it.
      </p>
    </div>
  </body>
</html>
"""

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        # Gmail App Password flow: connect plain, upgrade to TLS, then login.
        # smtplib.login() works correctly here — no custom auth challenge needed.
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(settings.mail_username, settings.mail_password)
            server.sendmail(settings.mail_from, to_email, msg.as_string())
