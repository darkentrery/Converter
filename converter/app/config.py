from pathlib import Path

from pydantic import SecretStr, field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(json_file='.json', extra='allow', case_sensitive=False, env_file='D:\\Python\\Converter\\.env')

    redis_host: str
    redis_port: int
    debug: bool = False

    database_username: str = Field(alias="POSTGRES_USER")
    database_password: SecretStr = Field(alias="POSTGRES_PASSWORD")
    database_host: str = Field(alias="POSTGRES_HOST")
    database_port: int = Field(alias="POSTGRES_PORT")
    database_name: str = Field(alias="POSTGRES_DB")

    cors_origins: str | list[str]

    is_test: bool | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        return v.replace(" ", '').split(',')

    @property
    def async_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.database_username}:{self.database_password.get_secret_value()}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def base_dir(self) -> str:
        return str(Path(__file__).resolve().parents[1])


config = Config()
