from urllib.parse import urlencode
import httpx
import logging
from src.config import settings

# Setup basic logging to see details in Docker logs
logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def build_google_auth_url(state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    """Trades the authorization code for access and refresh tokens."""
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=data)
        
        # THE FIX: Log the error body before raising exception
        if response.status_code != 200:
            print(f"\n--- GOOGLE OAUTH ERROR DETAILS ---")
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text}")
            print(f"Redirect URI being sent: {settings.google_redirect_uri}")
            print(f"----------------------------------\n")
            
        response.raise_for_status()
        return response.json()


async def get_google_user_info(access_token: str) -> dict:
    """Fetches user profile data using the access token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            print(f"GOOGLE USER INFO ERROR: {response.text}")
            
        response.raise_for_status()
        return response.json()