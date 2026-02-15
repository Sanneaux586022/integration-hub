from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from schemas.users import UserCreate
from fastapi import HTTPException


class userService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_user_by_email(self, email: str):
        user_query =  self.db.execute(select(User).filter(User.email == email))
        return user_query.scalar_one_or_none()

    async def create_user(self, user_input: UserCreate):
        try:
            existing_user = await self.get_user_by_email()

            if existing_user:
                raise HTTPException(status_code= 400, detail="Email già registrata")
            
            nuovo_utente = User(
                email= user_input.email,
                username = user_input.username,
                hashed_password = get_password_hash(user_input.password)
            )

            self.db.add(nuovo_utente)
            await self.db.commit()
            await self.db.refresh(nuovo_utente)
            return nuovo_utente
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Errore durante la registrazione : {str(e)}")


