from __future__ import annotations

import secrets
import string
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..config import get_settings
from ..db import get_session
from ..services.security import create_access_token

router = APIRouter(prefix="/groups", tags=["groups"])
settings = get_settings()


def _generate_pin() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


def _generate_token(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("", response_model=schemas.GroupResponse)
async def create_group(group: schemas.GroupCreate, session: AsyncSession = Depends(get_session)):
    new_group = models.Group(
        name=group.name,
        organizer_email=group.organizer_email,
        budget=group.budget,
        reveal_date=group.reveal_date,
        allow_household=group.allow_household,
        join_pin=_generate_pin(),
        join_token=_generate_token(),
    )
    organizer = models.Member(
        name="Organizer",
        email=group.organizer_email,
        is_organizer=True,
    )
    new_group.members.append(organizer)
    session.add(new_group)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group creation failed") from exc
    await session.refresh(new_group)

    join_url = f"{settings.public_base_url.rstrip('/')}/join?g={new_group.id}&t={new_group.join_token}"

    response = schemas.GroupResponse(
        id=new_group.id,
        join_url=join_url,
        join_pin=new_group.join_pin,
        join_token=new_group.join_token,
    )
    return response


@router.post("/{group_id}/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_group(
    group_id: uuid.UUID,
    member: schemas.MemberCreate,
    session: AsyncSession = Depends(get_session),
):
    query = select(models.Group).where(models.Group.id == group_id)
    result = await session.execute(query)
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if member.pin != group.join_pin or member.token != group.join_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid join credentials")

    new_member = models.Member(
        group_id=group_id,
        name=member.name,
        email=member.email,
        household=member.household,
        interests=member.interests,
        nogos=member.nogos,
    )
    session.add(new_member)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member already joined") from exc

    return None


@router.post("/{group_id}/token")
async def issue_token(group_id: uuid.UUID):
    token = create_access_token(group_id)
    return {"access_token": token, "token_type": "bearer"}
