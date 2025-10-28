import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(Text, nullable=False)
    organizer_email = Column(Text, nullable=False)
    budget = Column(Integer, nullable=True)
    reveal_date = Column(DateTime(timezone=True), nullable=True)
    allow_household = Column(Boolean, default=False)
    join_pin = Column(String(6), nullable=False)
    join_token = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    members = relationship("Member", cascade="all, delete-orphan", back_populates="group")
    exclusions = relationship("Exclusion", cascade="all, delete-orphan", back_populates="group")
    assignments = relationship("Assignment", cascade="all, delete-orphan", back_populates="group")


class Member(Base):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"))
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    household = Column(Text, nullable=True)
    interests = Column(ARRAY(Text), nullable=True)
    nogos = Column(ARRAY(Text), nullable=True)
    is_organizer = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    group = relationship("Group", back_populates="members")
    given_assignments = relationship("Assignment", foreign_keys="Assignment.giver_id", back_populates="giver")
    received_assignments = relationship("Assignment", foreign_keys="Assignment.receiver_id", back_populates="receiver")


class Exclusion(Base):
    __tablename__ = "exclusions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"))
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"))
    excluded_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"))

    group = relationship("Group", back_populates="exclusions")
    member = relationship("Member", foreign_keys=[member_id])
    excluded_member = relationship("Member", foreign_keys=[excluded_member_id])


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"))
    giver_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"))

    group = relationship("Group", back_populates="assignments")
    giver = relationship("Member", foreign_keys=[giver_id], back_populates="given_assignments")
    receiver = relationship("Member", foreign_keys=[receiver_id], back_populates="received_assignments")


class AnonymousMessage(Base):
    __tablename__ = "anon_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"))
    from_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="SET NULL"))
    to_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="SET NULL"))
    direction = Column(String(1), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    group = relationship("Group")
    sender = relationship("Member", foreign_keys=[from_member_id])
    recipient = relationship("Member", foreign_keys=[to_member_id])
