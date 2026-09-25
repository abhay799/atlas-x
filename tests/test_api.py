from pathlib import Path

from fastapi.testclient import TestClient

from atlas.api.app import create_app
from atlas.shared.config import Settings

ROOT = Path(__file__).parents[1]


def test_health_ready_and_core_flow():
    app = create_app(Settings(constitution_path=str(ROOT / "config/constitution.json")))
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").json()["status"] == "ready"
        assert client.post("/capabilities", json={"name": "data.analysis"}).status_code == 201
        agent = {
            "agent_id": "api-agent-1",
            "role": "Data",
            "authority": 2,
            "declared_capabilities": ["data.analysis"],
            "identity_provenance": "human-admin",
        }
        assert client.post("/agents", json=agent).status_code == 201
        assert client.post("/agents/api-agent-1/capabilities/data.analysis").status_code == 204
        response = client.post(
            "/missions/compile",
            json={"objective": "Investigate checkout conversion safely", "constraints": []},
        )
        assert response.status_code == 201
        mission = response.json()
        decision = client.post(
            "/governance/evaluate",
            json={
                "mission_id": mission["mission_id"],
                "task_id": "investigate-data",
                "agent_id": "api-agent-1",
            },
        )
        assert decision.status_code == 200
        assert decision.json()["outcome"] == "ALLOW"


def test_cors_default_origins():
    app = create_app(Settings(constitution_path=str(ROOT / "config/constitution.json")))
    with TestClient(app) as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_custom_origins(monkeypatch):
    monkeypatch.setenv("ATLAS_CORS_ORIGINS", "https://example.com,http://localhost:3000")
    # Need to reload the app to pick up the env var
    from importlib import reload

    import atlas.api.app
    reload(atlas.api.app)
    app = create_app(Settings(constitution_path=str(ROOT / "config/constitution.json")))
    with TestClient(app) as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "https://example.com"
        # Also test the second origin
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_effective_database_url_sqlite_fallback():
    # When POSTGRES_URL is empty, should fall back to DATABASE_URL
    settings = Settings(
        database_url="sqlite+pysqlite:///local.db",
        postgres_url="",
    )
    assert settings.effective_database_url == "sqlite+pysqlite:///local.db"


def test_effective_database_url_prefers_postgres():
    # When POSTGRES_URL is non-empty, should use it regardless of DATABASE_URL
    settings = Settings(
        database_url="sqlite+pysqlite:///local.db",
        postgres_url="postgresql+psycopg://user:pass@host/db",
    )
    assert settings.effective_database_url == "postgresql+psycopg://user:pass@host/db"


def test_effective_database_url_ignores_whitespace_postgres():
    # Whitespace-only POSTGRES_URL should be treated as empty (fallback)
    settings = Settings(
        database_url="sqlite+pysqlite:///local.db",
        postgres_url="   \t\n  ",
    )
    assert settings.effective_database_url == "sqlite+pysqlite:///local.db"
