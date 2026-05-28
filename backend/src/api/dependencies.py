from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.core.database import database



SessionDep = Annotated[AsyncSession, Depends(database.get_session)]