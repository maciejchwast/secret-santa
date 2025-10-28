from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..db import get_session
from ..services.security import get_current_group_id

router = APIRouter(prefix="/groups", tags=["members"])


@router.get("/{group_id}/members", response_model=list[schemas.MemberRead])
async def list_members(
    group_id: uuid.UUID,
    current_group_id: uuid.UUID = Depends(get_current_group_id),
    session: AsyncSession = Depends(get_session),
):
    if current_group_id != group_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = select(models.Member).where(models.Member.group_id == group_id)
    result = await session.execute(query)
    members = result.scalars().all()
    return [
        schemas.MemberRead(
            id=member.id,
            name=member.name,
            email=member.email,
            household=member.household,
            interests=member.interests or [],
            nogos=member.nogos or [],
            created_at=member.created_at,
            is_organizer=member.is_organizer,
        )
        for member in members
    ]


@router.post("/{group_id}/exclusions", status_code=status.HTTP_204_NO_CONTENT)
async def set_exclusions(
    group_id: uuid.UUID,
    payload: schemas.ExclusionPairs,
    current_group_id: uuid.UUID = Depends(get_current_group_id),
    session: AsyncSession = Depends(get_session),
):
    if current_group_id != group_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    query = select(models.Member.id).where(models.Member.group_id == group_id)
    result = await session.execute(query)
    member_ids = {row[0] for row in result.all()}
    for pair in payload.pairs:
        if len(pair) != 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pair payload")
        if not all(member_id in member_ids for member_id in pair):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member not in group")

    await session.execute(
        models.Exclusion.__table__.delete().where(models.Exclusion.group_id == group_id)
    )

    exclusions = [
        models.Exclusion(group_id=group_id, member_id=pair[0], excluded_member_id=pair[1])
        for pair in payload.pairs
    ]
    session.add_all(exclusions)
    await session.commit()
    return None
