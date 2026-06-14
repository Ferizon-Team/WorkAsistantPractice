from pydantic import BaseModel, Field
from typing import Optional


class STTRequest(BaseModel):
    audio_path: str


class STTResult(BaseModel):
    text: str
    text_length: int = Field(ge=0)
    language: Optional[str] = None
    confidence: Optional[float] = None

class STTRequestAPI(BaseModel):
    audio_base64: str = Field(..., description="Аудиофайл, закодированный в Base64")
    file_name: Optional[str] = Field(None, description="Необязательное имя файла для сохранения")
