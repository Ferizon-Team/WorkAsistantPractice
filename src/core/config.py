from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, PostgresDsn
from dotenv import load_dotenv
import os
load_dotenv()


class RunConfig(BaseSettings):
    
    host : str = "localhost"
    port : int = 8000


class S3Config(BaseSettings):
    url : str = Field(alias="S3_URL")
    access_id : str = Field(alias="S3_ACCESS_KEY_ID")
    secret_key : str = Field(alias="S3_ACCESS_SECRET")
    bucket_name : str = Field(alias="S3_BUCKET_NAME")
    save_file_url : str = Field(alias="S3_SAVE_FILE_URL")


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
    S3 : S3Config = S3Config()
    database : DataBaseConfig = DataBaseConfig()


settings = Settings()
# DB_HOST = os.environ["DB_HOST"]
# DB_PORT = os.environ["DB_PORT"]
# DB_USER = os.environ["DB_USER"]
# DB_PASS = os.environ["DB_PASS"]
# DB_NAME = os.environ["DB_NAME"]

# S3_URL = os.environ["S3_URL"]
# S3_ACCESS_KEY_ID = os.environ["S3_ACCESS_KEY_ID"]
# S3_ACCESS_SECRET = os.environ["S3_ACCESS_SECRET"]
# S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
# S3_SAVE_FILE_URL = os.environ["S3_SAVE_FILE_URL"]

# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"