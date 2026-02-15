from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func 
from app.db.database import Base

class User(Base):
    __tablename__= "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    hashed_password = Column(String(60), nullable=False)
    createAt = Column(DateTime(timezone=True), server_default=func.now())
    modifyAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (f"<User(username= '{self.username}', email= '{self.email}'," \
        " createAt = '{self.createAt}', lastchange= '{self.modifyAt}')>")
    