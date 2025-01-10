from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP,Text
from sqlalchemy.orm import relationship
from app.db_connection import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    is_group = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    _name = Column(String(100), nullable=False)

    last_message_id = Column(Integer, nullable=True)
    last_message_time = Column(TIMESTAMP, nullable=True)

    members = relationship("ChatMember", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship('Message', back_populates='chat', cascade='all, delete-orphan')

class ChatMember(Base):
    __tablename__ = "chat_members"

    chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String, default="member")

    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chats")
