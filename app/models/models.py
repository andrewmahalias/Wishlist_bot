from sqlalchemy import Column, Integer, String, Float, ForeignKey, BigInteger, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

family_members = Table(
    'family_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('family_id', Integer, ForeignKey('families.id'), primary_key=True),
    Column('role', String(20), default='member'),  # member, admin
    Column('joined_at', DateTime, server_default=func.now())
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)  # BigInteger!
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    wishes = relationship("Wish", back_populates="user", cascade="all, delete-orphan")

    families = relationship("Family", secondary=family_members, back_populates="members")


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    invite_code = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    members = relationship("User", secondary=family_members, back_populates="families")


class Wish(Base):
    __tablename__ = "wishes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    link = Column(String(255))
    price = Column(Float)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="wishes")
