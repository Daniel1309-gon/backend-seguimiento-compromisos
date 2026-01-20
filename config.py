from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    ID_APLICACION_CLIENTE: str
    ID_DIRECTORIO: str
    AZURE_APP_URI: str
    SCOPE_NAME: str = "access_as_user"
    FULL_SCOPE_URI: str
    ADMIN_USER_PASANTE: str
    ADMIN_USER_AUDITOR: str

    REDIS_URL: str
    REDIS_PASSWORD: str | None = None



    @property
    def database_url(self) -> str:
        return URL.create(
            drivername="postgresql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME
        )

settings = Settings()