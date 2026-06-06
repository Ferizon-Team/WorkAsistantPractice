from pydantic import BaseModel, Field
from typing import Optional


class STTRequest(BaseModel):
    audio_path: str


class STTResult(BaseModel):
    text: str
    text_length: int = Field(ge=0)
    language: Optional[str] = None
    confidence: Optional[float] = None
