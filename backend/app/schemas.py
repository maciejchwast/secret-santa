from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class GroupCreate(BaseModel):
    name: str
    organizer_email: EmailStr
    budget: Optional[int] = None
    reveal_date: Optional[datetime] = None
    allow_household: bool = False


class GroupResponse(BaseModel):
    group_id: uuid.UUID = Field(..., alias="id")
    join_url: str
    join_pin: str
    join_token: str

    class Config:
        allow_population_by_field_name = True


class MemberBase(BaseModel):
    name: str
    email: EmailStr
    household: Optional[str] = None
    interests: Optional[List[str]] = None
    nogos: Optional[List[str]] = None


class MemberCreate(MemberBase):
    pin: str
    token: str


class MemberRead(MemberBase):
    id: uuid.UUID
    created_at: datetime
    is_organizer: bool


class ExclusionPairs(BaseModel):
    pairs: List[List[uuid.UUID]]


class DrawResponse(BaseModel):
    status: str
    assigned: int


class AnonymousMessageCreate(BaseModel):
    from_member_id: uuid.UUID
    question: Optional[str] = None
    answer: Optional[str] = None

    def get_body(self) -> str:
        return self.question or self.answer or ""


class AnonymousRelayResponse(BaseModel):
    status: str
