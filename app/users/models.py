from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db_connection import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(Text)
    created_at = Column(TIMESTAMP, nullable=True)

    # Связь с чатами через chat_members
    chats = relationship("ChatMember", back_populates="user")
    messages = relationship("Message", back_populates="sender")