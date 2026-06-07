from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str
    file_name: str | None = None


class TTSResult(BaseModel):
    audio_path: str
    file_name: str
    format: str
    text_length: int = Field(ge=0)