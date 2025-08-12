"""
Base database models and configurations
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()


class TimestampMixin:
    """Mixin for adding timestamp fields"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin for UUID primary keys"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())