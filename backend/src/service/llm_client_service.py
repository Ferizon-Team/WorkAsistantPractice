import aiohttp
import logging
import json

from src.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClientService:
	def __init__(self,
				 base_url : str,
				 model_name : str):

		self.base_url = base_url.rstrip("/")
		self.model_name = model_name
		self.endpoint_url = f"{self.base_url}/api/generate"

		self.default_params = {
			"temperature": 0.1,
			"top_p": 0.9,
			"top_k": 40,
			"num_predict": 512,
			"repeat_penalty": 1.1,
			"stop": ["\n\n\n", "Контекст:"],
			}

	async def pull_model(self) -> bool:
		"""Загрузка модели в Ollama (если ещё не загружена)"""
		try:
			async with aiohttp.ClientSession() as session:
				payload = {"name": self.model_name}
				async with session.post(
						f"{self.base_url}/api/pull",
						json = payload,
						timeout = aiohttp.ClientTimeout(total = 300)
						) as response:
					if response.status == 200:
						return True
					else:
						return False
		except Exception as e:
			return False

	async def check_health(self) -> bool:
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(
						f"{self.base_url}/api/tags",
						timeout = aiohttp.ClientTimeout(total = 5)
						) as response:
					if response.status != 200:
						return False

					data = await response.json()
					models = [m["name"] for m in data.get("models", [])]

					model_exists = any(
						m.startswith(self.model_name.split(':')[0])
						for m in models
						)

					return model_exists

		except Exception as e:
			return False

	async def generate(self,
					   prompt : str,
					   system_prompt : str | None = None,
					   temperature: float| None = None,
					   max_tokens: int | None = None,
						   ) -> str:

		if system_prompt:
			full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
		else:
			full_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

		params = self.default_params.copy()
		if temperature is not None:
			params["temperature"] = temperature
		if max_tokens is not None:
			params["num_predict"] = max_tokens

		payload = {
			"model": self.model_name,
			"prompt": full_prompt,
			"stream": False,
			**params
			}

		try:
			async with aiohttp.ClientSession() as session:
				async with session.post(
						self.endpoint_url,
						json=payload,
					    timeout=aiohttp.ClientTimeout(total=30)
						) as response:

					if response.status != 200:
						error_text = await response.text()
						logger.error(f"Error while generate response: {error_text}")
						return self._fallback_response()

					result = await response.json()
					generated_text = result.get("response").strip()
					generated_text = self._clean_response(generated_text)

					return generated_text

		except aiohttp.ClientError as ex:
			logger.error(f"Error while generate response: {ex}")
			return self._fallback_response()

		except Exception as ex:
			logger.error(f"Error while generate response: {ex}")
			return self._fallback_response()

	@staticmethod
	def _clean_response(text: str) -> str:

		text = text.replace("<|im_end|>", "")
		text = text.replace("<|im_start|>", "")
		text = text.replace("assistant", "")

		while "\n\n\n" in text:
			text = text.replace("\n\n\n", "\n\n")

		return text.strip()

	@staticmethod
	def _fallback_response() -> str:
		"""Запасной ответ при ошибках"""
		return (
			"Извините, возникла техническая проблема при обработке запроса. "
			"Пожалуйста, попробуйте позже или обратитесь в HR-отдел."
		)


llm_client = OllamaClientService(
        base_url=f"http://{settings.model.ollama_host}:11434",
        model_name=settings.model.ollama_model,
    )

