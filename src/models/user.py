from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base




class User(Base):
    __tablename__ = "user"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(nullable=True,default=None)
    surname : Mapped[str] = mapped_column(nullable=True, default=None)