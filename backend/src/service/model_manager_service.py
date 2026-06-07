import logging
from pathlib import Path
from typing import Optional, Any
from faster_whisper import WhisperModel

from src.core.config import settings


logger = logging.getLogger(__name__)


class SileroTTSAdapter:
    """
    Адаптер для Silero TTS.
    """

    def __init__(
        self,
        model: Any,
        speaker: str = "baya",
        sample_rate: int = 48000,
    ):
        self.model = model
        self.speaker = speaker
        self.sample_rate = sample_rate

    def tts_to_file(self, text: str, file_path: str) -> None:
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.model.save_wav(
            text=text,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            audio_path=str(output_path),
        )


class ModelManager:
    
    """
    Управление загрузкой и кэшированием моделей.
    """

    def __init__(self):
        self.cache_dir = Path(settings.model.model_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._bge_model = None
        self._tts_model = None
        self._stt_model = None

        logger.info(f"Model cache: {self.cache_dir}")

    def get_bge_model(self) -> Optional[Any]:
        if self._bge_model is not None:
            return self._bge_model

        bge_path = self.cache_dir / "bge-m3"

        if bge_path.exists() and any(bge_path.iterdir()):
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading BGE-M3 from cache...")
                self._bge_model = SentenceTransformer(str(bge_path))
                logger.info("BGE-M3 loaded from cache")
                return self._bge_model

            except Exception as e:
                logger.error(f"Failed to load BGE-M3 from cache: {e}")

        else:
            logger.warning(f"BGE-M3 not found in cache: {bge_path}")
            logger.warning("Download the model on host machine first:")
            logger.warning("python scripts/download_models.py")

        return None

    def get_tts_model(self) -> Optional[Any]:
        """
        Загружает локальную TTS-модель.
        """

        if self._tts_model is not None:
            return self._tts_model

        tts_cache_path = Path("./models") / "torch_hub"

        if not tts_cache_path.exists():
            logger.warning(f"Silero TTS cache not found: {tts_cache_path}")
            logger.warning("Download the model on host machine first:")
            logger.warning("python scripts/download_models.py")
            return None

        try:
            import torch

            torch.hub.set_dir(str(tts_cache_path))

            logger.info("Loading Silero TTS from cache...")

            raw_tts_model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-models",
                model="silero_tts",
                language="ru",
                speaker="v4_ru",
            )

            self._tts_model = SileroTTSAdapter(
                model=raw_tts_model,
                speaker="baya",
                sample_rate=48000,
            )

            logger.info("Silero TTS loaded from cache")
            return self._tts_model

        except Exception as e:
            logger.error(f"Failed to load Silero TTS: {e}")
            return None
    
    def get_stt_model(self):
        if self._stt_model is not None:
            return self._stt_model

        self._stt_model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )
        return self._stt_model
    

model_manager = ModelManager()