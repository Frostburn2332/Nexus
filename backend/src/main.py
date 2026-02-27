from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes import health, auth, users, invitations


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # This is a good place to initialize DB pools if needed later
    yield


app = FastAPI(
    title="Nexus",
    description="Multi-tenant user management API",
    version="0.1.0",
    lifespan=lifespan,
)

# --- THE FIX ---
# Define the list of allowed origins explicitly.
# We include both the setting and the raw localhost variations.
origins = [
    str(settings.frontend_url).rstrip("/"), # Remove trailing slash if present
    "http://localhost",                     # Standard Docker/Nginx port
    "http://localhost:80",                  # Explicit port 80
    "http://localhost:5173",                # Standard Vite Dev port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(invitations.router)