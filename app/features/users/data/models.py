from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.core.models.base import Base

# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     phone_num = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     role = Column(String)  # e.g., S, A1, A2, O
#     company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
#     is_active = Column(Boolean, default=True)
#     can_delete_government = Column(Boolean, default=False)
#     can_manage_government_admins = Column(Boolean, default=False)
#     can_manage_operators = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# class Log(Base):
#     __tablename__ = "logs"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     action = Column(String)
#     entity_type = Column(String)
#     entity_id = Column(Integer, nullable=True)
#     details = Column(String, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow)