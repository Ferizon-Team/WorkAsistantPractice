from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str
    file_name: str | None = None


class TTSResult(BaseModel):
    audio_path: str
    file_name: str
    format: str
    text_length: int = Field(ge=0)
    
class TTSResponse(BaseModel):
    audio_base64: str = Field(..., description="Содержимое аудиофайла, закодированное в Base64")
    file_name: str = Field(..., description="Имя сгенерированного файла")
    format: str = Field(..., description="Формат аудиофайла (например, wav)")
    text_length: int = Field(..., description="Длина обработанного текста")