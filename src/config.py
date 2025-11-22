from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class BotSettings(BaseModel):
    token: str


class Settings(BaseSettings):
    bot: BotSettings
    timezone_string: str = Field(default="Asia/Omsk", alias="timezone")

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_string)


settings = Settings()  # type: ignore[call-arg]
