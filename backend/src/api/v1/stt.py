import base64
import tempfile
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException

from src.schemas.stt_schema import STTRequestAPI, STTResult

router = APIRouter(prefix="/stt", tags=["STT"])


@router.post("/transcribe", response_model=STTResult, summary="Распознавание речи из аудио")
async def transcribe_audio(request: Request, body: STTRequestAPI):
    """
    Принимает аудио в формате base64, распознаёт речь и возвращает текст.
    """
    stt_service = request.app.state.stt_service

    try:
        # 1. Декодируем base64 в байты
        audio_bytes = base64.b64decode(body.audio_base64)

        # 2. Сохраняем во временный файл
        # STT сервис (Whisper) работает с файлами на диске
        suffix = ".wav"  # по умолчанию WAV, можно определять по содержимому
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