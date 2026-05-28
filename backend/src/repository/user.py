from src.api.dependencies import SessionDep
from src.models.user import User



class UserRepository:

    @staticmethod
    async def create_user(self, session : SessionDep):
        user = User(name = "example", surname = "example")
        session.add(user)
        await session.commit()


user_repository = UserRepository()