from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence

import numpy as np

from src.models.document import Document, DocumentChunk


class DocumentRepository:

	@staticmethod
	async def add_document(session: AsyncSession,
						   title : str,
						   category : str | None = None,
						   source_path : str | None = None,

							) -> Document:

		document = Document(title=title,
							category=category,
							source_path=source_path
							)

		session.add(document)
		await session.flush()
		await session.commit()

		return document

	@staticmethod
	async def add_chunks(session: AsyncSession,
	                     document_id : int,
	                     chunks : list[str],
	                     embeddings : list[np.ndarray],
						 ) -> list[DocumentChunk]:

		chunk_objects = []

		for i, (text, embedding) in enumerate(zip(chunks, embeddings)):
			if isinstance(embedding, np.ndarray):
				emb_list = embedding.flatten().tolist()  # <- гарантирует 1D
			else:
				emb_list = embedding
			chunk = DocumentChunk(
				document_id=document_id,
				chunk_text = text,
				embedding = emb_list,
				chunk_index = i
				)

			session.add(chunk)
			chunk_objects.append(chunk)

		await session.flush()
		await session.commit()

		return chunk_objects

	@staticmethod
	async def get_document_by_id(
			session: AsyncSession,
			document_id: int,
			) -> Document | None:

		query = (
			select(Document)
			.where(Document.id == document_id)
			)

		result = await session.execute(query)
		return result.scalar_one_or_none()

	@staticmethod
	async def get_list_document(
			session: AsyncSession,
			category_name : str | None = None
			) -> Sequence[Document]:

		query = select(Document)

		if category_name is not None:
			query = query.where(Document.category == category_name)

		result = await session.execute(query.order_by(Document.created_at.desc()))
		return result.scalars().all()

	async def delete_document_by_id(
			self,
			session: AsyncSession,
			document_id: int,
			) -> bool:

		doc = await self.get_document_by_id(session, document_id)
		if doc is not None:
			await session.delete(doc)
			await session.commit()

			return True

		return False

document_repository = DocumentRepository()