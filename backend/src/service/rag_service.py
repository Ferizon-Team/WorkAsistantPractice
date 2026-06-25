import re
from pathlib import Path
from typing import AsyncGenerator
import asyncio
import logging
import base64

from redis.asyncio import Redis
from torch.utils.hipify.hipify_python import InputError

from src.service.tts_service import TTSService
from src.schemas.document import StreamChunkAnswer, StreamContentAnswer
from src.service.embedding_model_service import EmbeddingModelService
from src.service.llm_client_service import OllamaClientService
from src.repository.document.document_repository import DocumentRepository
from src.repository.document.search_repository import SearchRepository
from src.schemas.rag import AnswerQuestionResponse, Source
import json

from sqlalchemy.ext.asyncio import AsyncSession


class RAGService:

	def __init__(self,
				 embedding_service : EmbeddingModelService,
				 llm_client : OllamaClientService,
				 search_repository : SearchRepository,
				 document_repository : DocumentRepository,
				 tts_service : TTSService,
				 data_not_found_audio_path : Path
				 ) -> None:

		if embedding_service is None or llm_client is None or search_repository is None or document_repository is None or tts_service is None or data_not_found_audio_path is None:
			raise InputError

		self.embedding_service = embedding_service
		self.llm_client = llm_client
		self.search_repository = search_repository
		self.document_repository = document_repository
		self.tts_service = tts_service

		self.system_prompt = """
		Ты - корпоративный ассистент OnboardAI компании. Твоя главная задача - помогать сотрудникам быстро находить информацию во внутренних документах.

		СТРОГИЕ ПРАВИЛА:
		1. Отвечай ТОЛЬКО на основе информации из предоставленного контекста
		2. Если в контексте нет ответа, скажи: "Я не нашел эту информацию в базе знаний. Обратитесь в HR-отдел."
		3. Не придумывай процедуры, правила или контакты, которых нет в документах
		4. Если вопрос не по теме работы компании, вежливо откажись отвечать
		5. Отвечай по делу.
		6. Отвечай так как буд то перед тобой сидит тот кто задает вопрос. А ты тот кто отвечает. Без лишних служебных предложений и слов.
		"""

		if not data_not_found_audio_path.exists():
			self.data_not_found_audio_base64 = self.tts_service.synthesize_base64("Я не нашел эту информацию в базе знаний. Обратитесь в HR отдел", data_not_found_audio_path.name)

		else:
			with open(data_not_found_audio_path, "rb") as f:
				self.data_not_found_audio_base64 = base64.b64encode(f.read()).decode("utf-8")

	async def answer_question(self,
	                          redis_connect : Redis,
	                          session : AsyncSession,
	                          question : str,
	                          category : str | None = None
	                          ) -> AnswerQuestionResponse:

		query_embedding = await self.embedding_service.encode_async(question)

		relevant_chunks = await self.search_repository.semantic_search(
			session = session,
			query_embedding = query_embedding,
			top_k = 3,
			min_similarity = 0.65,
			category_filter = category
			)

		if not relevant_chunks:
			return AnswerQuestionResponse(
				answer = (
					"Я не нашел эту информацию в базе знаний."
					"Обратитесь в HR отдел"
				),
				sources = [],
				confidence = 0.0,
				context_used = 0
				)

		context_parts = []
		chunk_ids = []
		for chunk in relevant_chunks:
			context_parts.append(
				f"Документ: {chunk.title}\n"
				f"Содержание: {chunk.text}\n"
				f"---"
				)

			chunk_ids.append(chunk.id)

		#Сортируем chunk id что бы порядок всегда был одинаков
		chunk_ids.sort()

		#Генерируем ключ
		cache_key = "answer:" + "".join([str(i) for i in chunk_ids])

		cache_answer = await redis_connect.get(cache_key)

		#Если результат в кеше то отдаем его
		if cache_answer is not None:
			answer_schema_cache = AnswerQuestionResponse.model_validate_json(cache_answer)
			return answer_schema_cache
		context = "\n".join(context_parts)
		prompt = f"""
Контекст из базы знаний компании:

{context}

Вопрос сотрудника: {question}

Дай точный не сухой ответ, используя только информацию из контекста выше"""

		answer = await self.llm_client.generate(
			prompt = prompt,
			system_prompt = self.system_prompt,
			temperature = 0.1,
			max_tokens = 256,
			)

		max_similarity = max(chunk.similarity for chunk in relevant_chunks)

		answer_schema =  AnswerQuestionResponse(
			answer = answer,
			sources = [
				Source(
					id = chunk.id,
					title = chunk.title,
					similarity = round(chunk.similarity, 3),
					snippet = chunk.text[:150] + "..." if len(chunk.text) > 150 else chunk.text

					)
				for chunk in relevant_chunks
				],
			confidence = round(max_similarity, 3),
			context_used = len(relevant_chunks)
			)

		#Сохраняем результат
		ttl = 60 * 60 * 24
		await redis_connect.setex(cache_key, ttl, answer_schema.model_dump_json())

		return answer_schema


	async def answer_question_stream(self,
                                     redis_connect: Redis,
                                     session: AsyncSession,
                                     question: str,
                                     category: str | None = None
                                     ) -> AsyncGenerator[StreamChunkAnswer, None]:

		query_embedding = await self.embedding_service.encode_async(question)

		relevant_chunks = await self.search_repository.semantic_search(
            session=session,
            query_embedding=query_embedding,
            top_k=3,
            min_similarity=0.65,
            category_filter=category
        	)

		if not relevant_chunks:
			yield StreamChunkAnswer(
				event = "search.not_found",
				content = StreamContentAnswer(
					text = "Я не нашел эту информацию в базе знаний."
					"Обратитесь в HR отдел",
					media = self.data_not_found_audio_base64
					)
				)
			return

		context_parts = []
		chunk_ids = []

		for chunk in relevant_chunks:
			context_parts.append(
				f"Документ: {chunk.title}\n"
				f"Содержание: {chunk.text}\n"
				f"---"
				)

			chunk_ids.append(chunk.id)

		# Сортируем chunk id что бы порядок всегда был одинаков
		chunk_ids.sort()

		# Генерируем ключ
		cache_key = "answer:" + ":".join([str(i) for i in chunk_ids])

		cache_answer = await redis_connect.get(cache_key)

		if isinstance(cache_answer, bytes):
			cache_answer = cache_answer.decode("utf-8")

		# Если результат в кеше то отдаем его
		if cache_answer is not None:

			# Сигнал для фронта что бы структурировать сообщения
			yield StreamChunkAnswer(
				event = "llm.start",
				)
			try:
				cached_data = json.loads(cache_answer)
				answer_text = cached_data.get("answer", "")
			except json.JSONDecodeError:
				answer_text = cache_answer  # fallback если не JSON
			

			sentences = self._split_into_sentences(answer_text)
			for sentence in sentences:
				audio = self._safe_tts_synthesize(sentence)
				yield StreamChunkAnswer(
					event="llm.token",
					content=StreamContentAnswer(
						text=sentence + " ",
						media=audio
					)
				)
				await asyncio.sleep(0.05)

			yield StreamChunkAnswer(
				event = "llm.finish",
				)
			return

		context = "\n".join(context_parts)
		prompt = f"""
		Контекст из базы знаний компании:

		{context}

		Вопрос сотрудника: {question}

		Дай точный не сухой ответ, используя только информацию из контекста выше"""

		#Сигнал для фронта что бы структурировать сообщения
		yield StreamChunkAnswer(
				event = "llm.start",
				)
		text_buffer = ""
		parts = []
		async for chunk in self.llm_client.generate_stream(
				prompt = prompt,
				system_prompt = self.system_prompt,
				temperature = 0.1,
				max_tokens = 256,
				):
			parts.append(chunk)
			text_buffer += chunk

			while True:
				sentence, text_buffer = self._extract_sentence(text_buffer)
				if sentence is None:
					break

				audio = self._safe_tts_synthesize(sentence)
				yield StreamChunkAnswer(
					event="llm.token",
					content=StreamContentAnswer(
						text=sentence + " ",
						media=audio
					)
				)
		if text_buffer.strip():
				audio = self._safe_tts_synthesize(text_buffer.strip())
				yield StreamChunkAnswer(
					event="llm.token",
					content=StreamContentAnswer(
						text=text_buffer,
						media=audio
					)
				)


		yield StreamChunkAnswer(
				event = "llm.finish",
				)
		full_answer = "".join(parts)

		if full_answer.strip():
			# Сохраняем результат
			ttl = 60 * 60 * 24
			cache_data = {"answer": full_answer}
			await redis_connect.setex(
				cache_key, 
				ttl, 
				json.dumps(cache_data, ensure_ascii=False)
			)



	def _safe_tts_synthesize(self, text: str) -> str:
		"""
        Безопасный синтез TTS. Возвращает пустую строку вместо исключения.
        """
		if not text or not text.strip():
			return ""
		try:
			return self.tts_service.synthesize_base64(text.strip())
		except Exception as e:
            # Логируем, но не ломаем стрим
			logging.warning(f"TTS synthesis failed for text '{text[:50]}...': {e}")
			return ""

	def _split_into_sentences(self, text: str) -> list[str]:
		"""
        Разбивает текст на предложения по . ! ? \n
        """
        # Нормализуем разделители
		# text = text.replace('!', '.').replace('?', '.')
        # Разбиваем по точке с пробелом или переносу строки
		raw = re.split(r'[.\n]+', text)
		return [s.strip() for s in raw if s.strip()]

	def _extract_sentence(self, buffer: str) -> tuple[str | None, str]:
		"""
        Вытаскивает первое законченное предложение из буфера.
        Возвращает (sentence, оставшийся_буфер) или (None, buffer) если нет готового.
        """
        # Ищем ближайший разделитель
		delimiters = ['.', '!', '?', '\n']
        
		min_pos = -1
		min_delim_len = 0
        
		for delim in delimiters:
			pos = buffer.find(delim)
			if pos != -1 and (min_pos == -1 or pos < min_pos):
				min_pos = pos
				min_delim_len = len(delim)
        
		if min_pos == -1:
			return None, buffer
        
		sentence = buffer[:min_pos + min_delim_len].strip()
		remaining = buffer[min_pos + min_delim_len:]
        
		return sentence, remaining



	async def load_document(self,
							session : AsyncSession,
							title : str,
							text : str,
							category : str | None = None
							) -> int:

		document = await self.document_repository.add_document(
			session = session,
			title = title,
			category = category,
			)

		chunks = self._chunk_text(
			text = text,
			)

		embeddings = await self.embedding_service.encode_async(
			texts = chunks
			)

		await self.document_repository.add_chunks(
			session = session,
			document_id = document.id,
			chunks = chunks,
			embeddings = embeddings,
			)

		return document.id

	@staticmethod
	def _split_long_paragraph(
							 text : str,
							 max_size : int) -> list:
		sentences = text.replace("!", ".").replace("?", ".").split(".")
		chunks = []
		current_chunk = ""

		for sent in sentences:
			sent = sent.strip()
			if not sent:
				continue

			if len(current_chunk) + len(sent) < max_size:
				current_chunk += sent + ". "

			else:
				if current_chunk:
					chunks.append(current_chunk.strip())

				current_chunk = sent + ". "

		if current_chunk:
			chunks.append(current_chunk.strip())

		return chunks


	def _chunk_text(self,
					text : str,
					max_chunk_size : int = 500,
					) -> list:

		paragraphs = text.split("\n\n")
		chunks = []

		for para in paragraphs:
			para = para.strip()
			if not para:
				continue

			if len(para) <= max_chunk_size:
				chunks.append(para)
			else:
				sub_chunks = self._split_long_paragraph(para, max_chunk_size)
				chunks.extend(sub_chunks)

		return chunks


