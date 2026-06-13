import base64
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.api.dependencies import STTServiceDep
from src.schemas.stt_schema import STTRequestAPI, STTResult

router = APIRouter(prefix="/stt", tags=["STT"])


@router.post("/transcribe", response_model=STTResult, summary="Распознавание речи из аудио")
async def transcribe_audio(body: STTRequestAPI, stt_service: STTServiceDep):
    """
    Принимает аудио в формате base64, распознаёт речь и возвращает текст.
    """
    try:
        # 1. Декодируем base64 в байты
        audio_bytes = base64.b64decode(body.audio_base64)

        # 2. Сохраняем во временный файл
        suffix = ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            # 3. Вызываем сервис распознавания
            result = stt_service.transcribe(audio_path=tmp_path)
            return result
        finally:
            # 4. Удаляем временный файл
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка STT сервиса: {str(e)}")