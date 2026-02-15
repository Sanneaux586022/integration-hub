from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.users import UserCreate


class userService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_user_by_email(self, email: str):
        email_query =  await self.db.execute(select(User).filter(User.email == email))
        print(email_query)
        return email_query.scalar_one_or_none()
    

    async def create_user(self, user_input: UserCreate):
        try:
            existing_user = await self.get_user_by_email(user_input.email)

            if existing_user:
                raise HTTPException(status_code= 400, detail="Email già registrata")
            
            nuovo_utente = User(
                email= user_input.email.lower(),
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
        
    async def authenticate_user(self, email: str, password: str):

        user = await self.get_user_by_email(email.lower())
        if not user:
            raise HTTPException(status_code=400, detail="Credenziali non valide")
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Credenziali non valide")

        return user
            



