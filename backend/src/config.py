from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://nexus:nexus_password@localhost:5432/nexus"

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"

    jwt_secret_key: str = "change-this-in-production"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    email_provider: str = "console"

    # Neo SMTP (used when email_provider = "neo")
    mail_server: str = ""
    mail_port: int = 465
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""

    app_env: str = "development"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
