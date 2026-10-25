from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.agents.registry import agent_registry
from app.core.scheduler import world_scheduler
from app.api.routes_agents import router as agents_router
from app.api.routes_tasks import router as tasks_router
from app.api.routes_skills import router as skills_router
from app.api.routes_world import router as world_router
from app.api.routes_approvals import router as approvals_router
from app.api.websocket import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    init_db()
    agent_registry.seed_default_agents()
    
    if settings.AUTO_TICK_ENABLED:
        world_scheduler.start()

    yield

    # Shutdown:
    world_scheduler.stop()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend Core for AI CITY — Autonomous Artificial Society & Digital Workforce",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (allows Unity / browser clients to interact)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(agents_router)
app.include_router(tasks_router)
app.include_router(skills_router)
app.include_router(world_router)
app.include_router(approvals_router)
app.include_router(ws_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "description": "AI CITY — Autonomous Artificial Society & Digital Workforce",
        "world_time": world_scheduler.get_world_time(),
        "population": len(agent_registry.get_all_agents()),
        "endpoints": {
            "health": "/health",
            "agents": "/agents",
            "tasks": "/tasks",
            "skills": "/skills",
            "world": "/world",
            "approvals": "/approvals",
            "ws_world": "/ws/world",
            "ws_agents": "/ws/agents"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "world_time": world_scheduler.get_world_time()
    }
