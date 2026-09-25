import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from atlas.application.service import AtlasService
from atlas.domain.models import AgentIdentity, Capability, GovernanceDecision, Mission
from atlas.governance.constitution import ConstitutionError, load_constitution
from atlas.identity.service import DuplicateAgentError
from atlas.shared.config import Settings


class MissionCompileRequest(BaseModel):
    objective: str = Field(min_length=5)
    constraints: tuple[str, ...] = ()


class GovernanceEvaluateRequest(BaseModel):
    mission_id: UUID
    task_id: str
    agent_id: str | None = None


def database_is_ready(url: str) -> bool:
    engine = None
    try:
        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, ValueError):
        return False
    finally:
        if engine is not None:
            engine.dispose()
    return True


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            constitution = load_constitution(cfg.constitution_path)
        except ConstitutionError:
            raise
        app.state.atlas = AtlasService(constitution)
        yield

    app = FastAPI(title="ATLAS X", version="0.1.0", lifespan=lifespan)

    # CORS configuration
    origins_env = os.getenv("ATLAS_CORS_ORIGINS", "")
    if origins_env:
        origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
    else:
        origins = ["http://localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    def service(request: Request) -> AtlasService:
        return cast(AtlasService, request.app.state.atlas)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready(request: Request) -> dict[str, str]:
        atlas = service(request)
        effective_url = cfg.effective_database_url
        if effective_url and not database_is_ready(effective_url):
            raise HTTPException(status_code=503, detail="configured database is unavailable")
        return {"status": "ready", "constitution_version": atlas.constitution.constitution_version}

    @app.get("/metrics", include_in_schema=False)
    def metrics(request: Request) -> Response:
        values = service(request).telemetry.metrics()
        lines = [f"{name} {value:g}" for name, value in sorted(values.items())]
        return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

    @app.post("/capabilities", response_model=Capability, status_code=201)
    def register_capability(capability: Capability, request: Request) -> Capability:
        return service(request).register_capability(capability)

    @app.post("/agents", response_model=AgentIdentity, status_code=201)
    def register_agent(agent: AgentIdentity, request: Request) -> AgentIdentity:
        try:
            return service(request).register_agent(agent)
        except DuplicateAgentError as exc:
            raise HTTPException(status_code=409, detail="agent already exists") from exc

    @app.get("/agents/{agent_id}", response_model=AgentIdentity)
    def get_agent(agent_id: str, request: Request) -> AgentIdentity:
        agent = service(request).agents.get(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail="agent not found")
        return agent

    @app.post("/agents/{agent_id}/capabilities/{capability_name}", status_code=204)
    def grant_capability(agent_id: str, capability_name: str, request: Request) -> None:
        try:
            service(request).grant_capability(agent_id, capability_name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/missions/compile", response_model=Mission, status_code=201)
    def compile_mission(body: MissionCompileRequest, request: Request) -> Mission:
        return service(request).compile_mission(body.objective, body.constraints)

    @app.get("/missions/{mission_id}", response_model=Mission)
    def get_mission(mission_id: UUID, request: Request) -> Mission:
        mission = service(request).get_mission(mission_id)
        if mission is None:
            raise HTTPException(status_code=404, detail="mission not found")
        return mission

    @app.post("/governance/evaluate", response_model=GovernanceDecision)
    def evaluate(body: GovernanceEvaluateRequest, request: Request) -> GovernanceDecision:
        try:
            return service(request).evaluate(body.mission_id, body.task_id, body.agent_id)
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
