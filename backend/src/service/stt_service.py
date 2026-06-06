from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel

from src.schemas.stt_schema import STTResult
from src.exceptions.stt_exceptions import (
    STTModelNotLoadedError,
    STTTranscriptionError,
)

class STTService:
    """
    Speech-To-Text сервис.
    аудио в текст
    """

    def init(
        self,
        model: Optional[WhisperModel],
        temp_dir: str = "storage/stt",
    ) -> None:
        self.model = model
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def transcribe(self, audio_path: str) -> STTResult:
        """
        Распознаёт речь из аудиофайла
        """

        if self.model is None:
            raise STTModelNotLoadedError("STT model is not loaded")

        try:
            segments, info = self.model.transcribe(audio_path)

            text = " ".join(seg.text for seg in segments).strip()

            return STTResult(
                text=text,
                text_length=len(text),
                language=getattr(info, "language", None),
                confidence=getattr(info, "language_probability", None),
            )

        except Exception as error:
            raise STTTranscriptionError(
                f"Failed to transcribe speech: {error}"
            ) from error
