from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, PostgresDsn
from dotenv import load_dotenv
import os
load_dotenv()


class RunConfig(BaseSettings):
    
    host : str = Field(alias="APP_HOST", default = "localhost")
    port : int  = Field(alias="APP_PORT", default = 8000)

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
    



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra = "ignore")
    run : RunConfig = RunConfig()
    database : DataBaseConfig = DataBaseConfig()


settings = Settings()