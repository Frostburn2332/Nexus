from .provider import EmailProvider
from .console import ConsoleEmailProvider


def get_email_provider(provider_name: str = "console") -> EmailProvider:
    providers = {
        "console": ConsoleEmailProvider,
    }

    provider_class = providers.get(provider_name)
    if provider_class is None:
        raise ValueError(f"Unknown email provider: {provider_name}. Available: {list(providers.keys())}")

    return provider_class()


__all__ = ["EmailProvider", "ConsoleEmailProvider", "get_email_provider"]
