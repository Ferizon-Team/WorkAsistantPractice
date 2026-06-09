from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import numpy as np

from src.models.document import Document, DocumentChunk
from src.schemas.document import SematicSearchResult


class SearchRepository:

	@staticmethod
	def _format_embedding(embedding: np.ndarray) -> str:
		"""Преобразует numpy массив в строку для pgvector"""
		emb = np.array(embedding).flatten()
		return "[" + ",".join(str(x) for x in emb) + "]"


	async def semantic_search(
			self,
			session: AsyncSession,
			query_embedding: np.ndarray,
			top_k: int = 3,
			min_similarity: float = 0.55,
			category_filter : str | None = None,
			) -> list[SematicSearchResult]:

		emb_str = self._format_embedding(query_embedding)
		params_dict = {
			"query_embedding": emb_str,
			"min_similarity": min_similarity,
			"top_k": top_k
			}


		category_clause = ""
		if category_filter is not None:
			params_dict["category"] = category_filter
			category_clause = "AND doc.category = :category"

		query = text(
			f"""
		            SELECT 
		                ch.id,
		                ch.chunk_text,
		                ch.chunk_index,
		                ch.metadata_json,
		                doc.title,
		                doc.category,
		                1 - (ch.embedding <=> :query_embedding) AS similarity
		            FROM document_chunks ch
		            JOIN documents doc ON ch.document_id = doc.id
		            WHERE 1 - (ch.embedding <=> :query_embedding) > :min_similarity
		            {category_clause}
		            ORDER BY ch.embedding <=> :query_embedding
		            LIMIT :top_k
		        """
			)


		result = await session.execute(query, params_dict)
		rows = result.fetchall()


		return [
			SematicSearchResult(
				id = row.id,
				text = row.chunk_text,
				title = row.title,
				category = row.category,
				similarity = float(row.similarity),
				chunk_index = row.chunk_index,
				metadata = row.metadata_json or {}
				)
			for row in rows
			]




search_repository = SearchRepository()