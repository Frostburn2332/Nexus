from .provider import EmailProvider


class ConsoleEmailProvider(EmailProvider):
    """Logs invitation emails to stdout. Swap for SendGrid/Resend in production."""

    async def send_invitation(self, to_email: str, inviter_name: str, organization_name: str, invitation_link: str) -> None:
        print(f"\n{'='*60}")
        print(f"  INVITATION EMAIL")
        print(f"  To:           {to_email}")
        print(f"  From:         {inviter_name} ({organization_name})")
        print(f"  Accept link:  {invitation_link}")
        print(f"{'='*60}\n")
