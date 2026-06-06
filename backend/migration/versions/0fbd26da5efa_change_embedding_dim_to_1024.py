"""change_embedding_dim_to_1024

Revision ID: 0fbd26da5efa
Revises: bcb9affdd402
Create Date: 2026-06-04 14:09:59.824196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fbd26da5efa'
down_revision: Union[str, None] = 'bcb9affdd402'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Меняем размерность с 768 на 1024
    op.execute("""
        ALTER TABLE document_chunks 
        ALTER COLUMN embedding TYPE VECTOR(1024)
    """)


def downgrade() -> None:
    # Откат обратно на 768
    op.execute("""
        ALTER TABLE document_chunks 
        ALTER COLUMN embedding TYPE VECTOR(768)
    """)