import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import overlay

app = FastAPI(title="QuackChat - Backend (Step 1)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Routes
app.include_router(overlay.router)

if os.getenv("ENV", "dev") != "prod":
    from app.api.routes import dev
    app.include_router(dev.router) 