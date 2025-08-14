from src.api.dependencies import SessionDep
from src.models.user import User



class UserRepository:
    @classmethod
    async def create_user(self, session : SessionDep):
        user = User(name = "AAA", surname = "BBB")
        session.add(user)
        await session.commit()