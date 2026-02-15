
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.user import User
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

# 1. Definiamo il contesto di crittografia
# Specifichiamo che vogliamo usare bcrypt e che deve gestire automaticamente
# la compatibilità con eventuali schemi deprecati in futuro
def verify_password(plain_password: str, hashed_password: str)-> bool:
    """
    Docstring for verify_password
    
    :param plain_password: Description
    :type plain_password: str
    :param hashed_password: Description
    :type hashed_password: str
    :return: Description
    :rtype: bool
    Confronta una password cin chiaro con l'hash salvato nel DB.
    Restituisce True se corrispondono, False altrimenti.
    """

    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str)-> str:
    """
    Trasforma una password in chiaro in una hash BCrypt.
    Questa è la funzione da usare durante la registrazione.
    """
    return pwd_context.hash(password)

def create_acces_token(data: dict, expires_delta: timedelta |None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


async def get_current_user_1(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_execptions = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Impossibile validare le credenziali",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. decodifichiamo il token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_execptions
    except JWTError:
        raise credentials_execptions
    
    # 2. Cerchiamo l'utente nel database
    query = await db.execute(select(User).filter(User.email == email))
    user = query.scalar_one_or_none()

    if user is None:
        raise credentials_execptions
    
    return user

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    # Abbiamo aggiunto la request per leggere i cookies  
    
    # 1. Prova a prendere il token dall'header Authorization
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer"):
        token = token.replace("Bearer ", "")
    else:
        # 2. Se non c'è nell'header , prova  prenderlo dai cookies
        token = request.cookies.get("access_token")

    if not token:
        # Invece di lanciare l'eccezione qui , restituiamo None
        # o gestiamo il redirect nelle rotta
        return None
    try: 
        # 1. decodifichiamo il token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")

            # 2. Cerchiamo l'utente nel database
        query = await db.execute(select(User).filter(User.email == email))
        user = query.scalar_one_or_none()
    
        return user
    except JWTError:
        return None