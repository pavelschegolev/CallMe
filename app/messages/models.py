from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db_connection import Base

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'))
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=True, default=None)

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('User', back_populates='messages')
