from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_", env_file=".env", extra="ignore")
    env: str = "development"
    constitution_path: str = "config/constitution.json"
    log_level: str = "INFO"
    database_url: str = ""
    postgres_url: str = ""

    @property
    def effective_database_url(self) -> str:
        """Return POSTGRES_URL if set and non-blank, otherwise fallback to DATABASE_URL."""
        postgres_url = self.postgres_url.strip()
        return postgres_url if postgres_url else self.database_url
