import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.api.dependencies import TTSServiceDep
from src.schemas.tts_schema import TTSRequest, TTSResponse

router = APIRouter(prefix="/tts", tags=["TTS"])


@router.post("/synthesize", response_model=TTSResponse, summary="Синтез речи из текста")
async def synthesize_speech(body: TTSRequest, tts_service: TTSServiceDep):
    """
    Принимает текст, генерирует аудио через TTSService и возвращает его в формате base64.
    """
    try:
        # 1. Вызываем сервис
        result = tts_service.synthesize(
            text=body.text,
            file_name=body.file_name
        )

        # 2. Читаем файл с диска
        audio_path = Path(result.audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Аудиофайл не был создан: {audio_path}")

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        # 3. Кодируем в base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        # 4. (Опционально) Удаляем временный файл
        # audio_path.unlink(missing_ok=True)

        # 5. Возвращаем ответ
        return TTSResponse(
            audio_base64=audio_base64,
            file_name=result.file_name,
            format=result.format,
            text_length=result.text_length
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка TTS сервиса: {str(e)}")