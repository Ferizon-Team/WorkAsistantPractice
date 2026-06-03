import logging
from pathlib import Path
from typing import Optional, Any

from src.core.config import settings


logger = logging.getLogger(__name__)
class ModelManager:
	"""
	Управление загрузкой и кэшированием моделей
	"""

	def __init__(self):
		self.cache_dir = Path(settings.model.model_cache_dir)
		self.cache_dir.mkdir(parents = True, exist_ok = True)

		self._bge_model = None

		logger.info(f"Model cache: {self.cache_dir}")

	def get_bge_model(self) -> Optional[Any]:
		if self._bge_model is not None:
			return self._bge_model

		bge_path = self.cache_dir / "bge-m3"

		# Проверяем кэш
		if bge_path.exists() and any(bge_path.iterdir()):
			try:
				from sentence_transformers import SentenceTransformer

				logger.info("Loading BGE-M3 from cache...")
				self._bge_model = SentenceTransformer(str(bge_path))
				logger.info("BGE-M3 loaded from cache")
				return self._bge_model
			except Exception as e:
				logger.error(f"Failed to load from cache: {e}")
		else:
			logger.warning(f"BGE-M3 not found in cache: {bge_path}")
			logger.warning("Download the model on host machine first:")
			logger.warning("python scripts/download_models.py")

		return None


model_manager = ModelManager()