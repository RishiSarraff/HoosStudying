from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, func, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from enum import Enum as PyEnum

class SenderType(str, PyEnum):
    user = 'user'
    bot = 'bot'

class TagType(str, PyEnum):
    system = 'system'
    custom = 'custom'

class User(Base):
    __tablename__ = "User"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Pipeline(Base):
    __tablename__ = "Pipeline"

    pipeline_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    pipeline_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Document(Base):
    __tablename__ = "Document"

    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    file_name: Mapped[str] = mapped_column(String(50), nullable=False)
    file_type: Mapped[str] = mapped_column(String(5), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(server_default=func.now())

class Document_Metadata(Base):
    __tablename__ = "Document_Metadata"

    metadata_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('Document.document_id', ondelete='CASCADE', onupdate='CASCADE'), unique=True, nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=True)
    page_count: Mapped[int] = mapped_column(nullable=True)
    word_count: Mapped[int] = mapped_column(nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=True)
    encoding:  Mapped[str] = mapped_column(String(50), nullable=True)
    firebase_storage_path: Mapped[str] = mapped_column(String(500), nullable=True)
    firebase_download_url: Mapped[str] = mapped_column(Text, nullable=True)
    checksum: Mapped[str] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Document_Chunk(Base):
    __tablename__ = "Document_Chunk"
    __table_args__ = (UniqueConstraint('document_id', 'chunk_index', name='unique_document_chunk'),)

    chunk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('Document.document_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Pipeline_Documents(Base):
    __tablename__ = "Pipeline_Documents"

    pipeline_id: Mapped[int] = mapped_column(ForeignKey('Pipeline.pipeline_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('Document.document_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default='1')

class Conversation(Base):
    __tablename__ = "Conversation"

    conversation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    pipeline_id: Mapped[int] = mapped_column(ForeignKey('Pipeline.pipeline_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_message_at: Mapped[datetime] = mapped_column()

class Message(Base):
    __tablename__ = "Message"

    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey('Conversation.conversation_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    sender_type: Mapped[str] = mapped_column(SQLEnum(SenderType), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())

class Tag(Base):
    __tablename__ = "Tag"
    __table_args__ = (UniqueConstraint('user_id', 'name', name='unique_user_tag'),)

    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id', ondelete='CASCADE'), nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    tag_type: Mapped[str] = mapped_column(SQLEnum(TagType), nullable=False, server_default='custom')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Pipeline_Tag(Base):
    __tablename__ = "Pipeline_Tag"

    pipeline_id: Mapped[int] = mapped_column(ForeignKey('Pipeline.pipeline_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('Tag.tag_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)