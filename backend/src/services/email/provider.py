from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    async def send_invitation(self, to_email: str, inviter_name: str, organization_name: str, invitation_link: str) -> None:
        """Send an invitation email with the accept link."""
