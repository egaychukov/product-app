from typing import Annotated

from pydantic import SecretStr, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT settings
    secret_key: SecretStr
    algorithm: str
    access_token_ttl: Annotated[int, Field(alias="ACCESS_TOKEN_TTL_MINUTES")]
    refresh_token_ttl: Annotated[int, Field(alias="REFRESH_TOKEN_TTL_MINUTES")]

    # Database settings
    db_username: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_name: str

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
        }
    )


settings = Settings()
