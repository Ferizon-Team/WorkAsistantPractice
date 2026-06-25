from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Optional, Protocol
from uuid import uuid4
from pydantic import BaseModel, Field
from num2words import num2words
from src.schemas.tts_schema import TTSResult
from src.exceptions.tts_exceptions import (
    TTSModelNotLoadedError,
    TTSSynthesisError,
)

class TTSService:
    """
    Сервис Text-To-Speech.

    Отвечает только за генерацию аудио из текста.
    """

    def __init__(
        self,
        model: Optional[TTSModelProtocol],
        output_dir: str="storage/tts",
        audio_format: str="wav",
    ) -> None:
        self.model = model
        self.output_dir = Path(output_dir)
        self.audio_format = audio_format
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, file_name: Optional[str] = None) -> TTSResult:
        """
        Args:
            text: Текст, который нужно озвучить.
            file_name: Необязательное имя файла. Если не передано,
                сервис создаст уникальное имя автоматически.
        """
        if self.model is None:
            raise TTSModelNotLoadedError("TTS model is not loaded")

        normalized_text = self._validate_text(text)
        # Преобразуем числа в слова перед отправкой в модель
        normalized_text = self._normalize_numbers(normalized_text)
        output_path = self._build_output_path(file_name)

        try:
            self.model.tts_to_file(
                text=normalized_text,
                file_path=str(output_path),
            )
        except Exception as error:
            raise TTSSynthesisError(
                f"Failed to synthesize speech: {error}"
            ) from error

        return TTSResult(
            audio_path=str(output_path),
            file_name=output_path.name,
            format=self.audio_format,
            text_length=len(normalized_text),
        )

    def synthesize_base64(self, text: str, file_name: Optional[str] = None) -> str:
        if not text or not text.strip():
            return ""

        result = self.synthesize(text, file_name)
        audio_path = Path(result.audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Аудиофайл не был создан: {audio_path}")

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        # Кодируем в base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return audio_base64

    def _validate_text(self, text: str) -> str:
        """
        Проверяет текст перед генерацией
        """
        normalized_text = text.strip()
        if not normalized_text:
            raise ValueError("Text for TTS synthesis cannot be empty")
        return normalized_text

    def _normalize_numbers(self, text: str) -> str:
        """
        Преобразует числа в слова для корректной озвучки.
        
        Например: "28" -> "двадцать восемь"
        """
        def replace_number(match):
            number = int(match.group())
            return num2words(number, lang='ru')
        
        # Находим все числа и заменяем их на слова
        return re.sub(r'\b\d+\b', replace_number, text)

    def _build_output_path(self, file_name: Optional[str] = None) -> Path:
        """
        путь для будущего аудиофайла
        """
        if file_name is None:
            file_name = f"{uuid4()}.{self.audio_format}"

        if not file_name.endswith(f".{self.audio_format}"):
            file_name = f"{file_name}.{self.audio_format}"

        return self.output_dir / file_name