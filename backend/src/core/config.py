from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn
from dotenv import load_dotenv
import os
load_dotenv()


class RunConfig(BaseSettings):
    
    host : str = Field(alias="APP_HOST", default = "localhost")
    port : int  = Field(alias="APP_PORT", default = 8000)

class ModelsConfig(BaseSettings):
    model_config = SettingsConfigDict(extra = "ignore")

    model_cache_dir: str = Field(
        default = "/app/models_cache",
        alias = "MODEL_CACHE_DIR"
        )
    ollama_host: str = Field(
        default = "ollama",
        alias = "OLLAMA_HOST"
        )
    ollama_model: str = Field(
        default = "qwen2.5:3b",
        alias = "OLLAMA_MODEL"
        )

class DataBaseConfig(BaseSettings):
    echo : bool = False
    echo_pool : bool = False
    max_overflow : int = 50
    pool_size : int = 10

    user : str = Field(alias="DB_USER")
    password : str = Field(alias="DB_PASS")
    host : str = Field(alias="DB_HOST")
    port : str = Field(alias="DB_PORT")
    db_name : str = Field(alias="DB_NAME")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
    
class RedisConfig(BaseSettings):
    host : str = Field(alias="REDIS_HOST")
    port : int = Field(alias="REDIS_PORT")
    db : str = Field(alias="REDIS_DB")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra = "ignore")

    model : ModelsConfig = ModelsConfig()
    run : RunConfig = RunConfig()
    database : DataBaseConfig = DataBaseConfig()
    cache : RedisConfig = RedisConfig()


settings = Settings()