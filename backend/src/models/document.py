from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from src.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, auto_increment=True)

    title : Mapped[str] = mapped_column(String(500), nullable=False)
    category : Mapped[str | None] = mapped_column(String(100), nullable=True)

    source_path : Mapped[str | None] = mapped_column(String(1000), nullable=True, comment = "Путь к исходному файлу")

    created_at : Mapped[datetime] = mapped_column(DateTime, server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default = func.now(), onupdate = func.now())

    chunks : Mapped[list["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", lazy = "selectin")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, auto_increment=True)

    document_id : Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete = "CASCADE"), nullable=False)
    chunk_text : Mapped[str] = mapped_column(Text, nullable=False)
    embedding : Mapped[Vector | None] = mapped_column(Vector(768), nullable=True, comment = "Векторный текст")
    chunk_index : Mapped[int] = mapped_column(Integer, comment = "Порядковый номер чанка в документе")
    metadata_json : Mapped[dict | None] = mapped_column(comment = "Дополнительные метаданные в json", default = {}, nullable = True)
    created_at : Mapped[datetime] = mapped_column(DateTime, server_default = func.now())

    document : Mapped[Document] = relationship("Document", back_populates="chunks")
