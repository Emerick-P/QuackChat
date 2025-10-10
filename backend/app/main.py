from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import overlay, auth, me, public, pairing
from app.core.redis_broker import RedisBroker
from app.core.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting up...")
    try:
        await broker.connect()
        app.state.redis_broker = broker
    except Exception as e:
        print(f"Error connecting to Redis broker: {e}")

    yield

    # Shutdown
    print("Application shutting down...")
    await broker.close()

broker = RedisBroker(settings.REDIS_URL)
app = FastAPI(title="QuackChat - Backend (Step 1)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Routes
app.include_router(overlay.router)
app.include_router(public.router)
app.include_router(me.router)
app.include_router(pairing.router)

if settings.ENV != "prod":
    from app.api.routes import dev
    app.include_router(dev.router) 
    app.include_router(auth.router)