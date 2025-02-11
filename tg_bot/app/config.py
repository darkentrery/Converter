from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(json_file='.json', extra='allow', case_sensitive=False, env_file='.env')

    A4_PORTRAIT: tuple[int, int] = (595, 842)  # Размер A4 в пикселях (72 DPI)
    A4_LANDSCAPE: tuple[int, int] = (842, 595)
    TG_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int


config = Config()
