from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    WEB_HOST: str
    WEB_PORT: int
    APP_STATIC_PATH: str
    APP_TEMPLATES_PATH: str
    SQL_ALCHEMY_DEBUG: bool
    SSL_CERT_ENABLED: bool
    SSL_CERT_PATH: str
    SSL_KEY_PATH: str

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=(".env.template", ".env"))

settings = Settings()