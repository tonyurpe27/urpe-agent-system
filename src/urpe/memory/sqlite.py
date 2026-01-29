"""SQLite-based conversation memory."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()


class Conversation(Base):
    """Conversation model."""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    model = Column(String, nullable=True)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")


class MemoryStore:
    """SQLite memory store for conversations."""
    
    def __init__(self, db_path: str = "data/urpe.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine)
    
    def create_conversation(self, model: Optional[str] = None) -> str:
        """Create a new conversation and return its ID."""
        session = self.Session()
        try:
            conv = Conversation(model=model)
            session.add(conv)
            session.commit()
            return conv.id
        finally:
            session.close()
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[list] = None,
    ) -> str:
        """Add a message to a conversation."""
        session = self.Session()
        try:
            msg = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_calls=json.dumps(tool_calls) if tool_calls else None,
            )
            session.add(msg)
            session.commit()
            return msg.id
        finally:
            session.close()
    
    def get_messages(self, conversation_id: str) -> List[dict]:
        """Get all messages for a conversation."""
        session = self.Session()
        try:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None,
                }
                for msg in messages
            ]
        finally:
            session.close()
    
    def get_conversations(self, limit: int = 10) -> List[dict]:
        """Get recent conversations."""
        session = self.Session()
        try:
            convs = session.query(Conversation).order_by(
                Conversation.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": conv.id,
                    "created_at": conv.created_at.isoformat(),
                    "model": conv.model,
                    "message_count": len(conv.messages),
                }
                for conv in convs
            ]
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get a conversation by ID."""
        session = self.Session()
        try:
            conv = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conv:
                return None
            
            return {
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "model": conv.model,
                "messages": self.get_messages(conversation_id),
            }
        finally:
            session.close()
    
    def close(self):
        """Close the database engine connection (important for Windows)."""
        self.engine.dispose()


# Default memory store instance
memory = MemoryStore()
