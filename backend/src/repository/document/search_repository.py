from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import numpy as np

from src.models.document import Document, DocumentChunk
from src.schemas.document import SematicSearchResult, HybridSearchResult


class SearchRepository:

	@staticmethod
	async def semantic_search(
			session: AsyncSession,
			query_embedding: np.ndarray,
			top_k: int = 3,
			min_similarity: float = 0.65,
			category_filter : str | None = None,
			) -> list[SematicSearchResult]:


		query = text("""
		SELECT 
			ch.chunk_text,
			ch.chunk_index,
			ch.metadata_json,
			doc.title,
			doc.category,
			1 - (ch.embedding <=> :query_embedding) AS similarity
			
		FROM chunks ch 
		JOIN documents doc ON ch.document_id = doc.document_id
		WHERE 1 - (c.embedding <=> :query_embedding) > :min_similarity
        {}
		ORDER BY ch.embedding <=> :query_embedding
		LIMIT :top_k
		""")

		params = {
			'query_embedding': query_embedding.tolist(),
			'min_similarity': min_similarity,
			'top_k': top_k,
			}

		if category_filter is not None:
			params['category'] = category_filter

		result = await session.execute(query, params)
		rows = result.fetchall()

		return [
			SematicSearchResult(
				text = row.chunk_text,
				title = row.title,
				category = row.category,
				similarity = float(row.similarity),
				chunk_index = row.chunk_index,
				metadata = row.metadata or {}
				)
			for row in rows
			]


	@staticmethod
	async def hybrid_search(
			session: AsyncSession,
			query_text: str,
			query_embedding: np.ndarray,
			top_k: int = 5
			) -> list[HybridSearchResult]:
		"""
		Гибридный поиск семантический + текстовый
		"""
		query = text(
			"""
            SELECT c.chunk_text,
                   d.title,
                   1 - (c.embedding <=> :query_embedding) AS semantic_similarity,
                   ts_rank(
                           to_tsvector('russian', c.chunk_text),
                           plainto_tsquery('russian', :query_text)
                   )                                      AS text_rank
            FROM chunks c
                     JOIN documents d ON c.document_id = d.id
            WHERE 1 - (c.embedding <=> :query_embedding) > 0.5
               OR to_tsvector('russian', c.chunk_text) @@ plainto_tsquery('russian'
                , :query_text)
            ORDER BY
                (1 - (c.embedding <=> :query_embedding)) * 0.7 +
                COALESCE (ts_rank(to_tsvector('russian', c.chunk_text),
                plainto_tsquery('russian', :query_text)), 0) * 0.3 DESC
                LIMIT :top_k
		             """
			)

		result = await session.execute(
			query, {
				"query_embedding": query_embedding.tolist(),
				"query_text": query_text,
				"top_k": top_k
				}
			)

		return [
			HybridSearchResult(
				text = row.chunk_text,
				 title = row.title,
				semantic_similarity = float(row.semantic_similarity),
				text_rank = float(row.text_rank) if row.text_rank else 0
		)
			for row in result
			]

search_repository = SearchRepository()