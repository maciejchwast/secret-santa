from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..db import get_session

router = APIRouter(prefix="/groups", tags=["anonymous"])


def _validate_membership(
    session: AsyncSession, group_id: uuid.UUID, member_id: uuid.UUID
):
    return session.execute(
        select(models.Member).where(
            models.Member.group_id == group_id, models.Member.id == member_id
        )
    )


@router.post("/{group_id}/anon", response_model=schemas.AnonymousRelayResponse)
async def send_anonymous_question(
    group_id: uuid.UUID,
    payload: schemas.AnonymousMessageCreate,
    session: AsyncSession = Depends(get_session),
):
    if not payload.question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question required")

    result = await session.execute(
        select(models.Assignment).where(
            models.Assignment.group_id == group_id,
            models.Assignment.giver_id == payload.from_member_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member not part of draw")

    anon = models.AnonymousMessage(
        group_id=group_id,
        from_member_id=payload.from_member_id,
        to_member_id=assignment.receiver_id,
        direction="q",
        body=payload.question,
    )
    session.add(anon)
    await session.commit()
    return schemas.AnonymousRelayResponse(status="ok")


@router.post("/{group_id}/anon/reply", response_model=schemas.AnonymousRelayResponse)
async def send_anonymous_answer(
    group_id: uuid.UUID,
    payload: schemas.AnonymousMessageCreate,
    session: AsyncSession = Depends(get_session),
):
    if not payload.answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answer required")

    result = await session.execute(
        select(models.Assignment).where(
            models.Assignment.group_id == group_id,
            models.Assignment.receiver_id == payload.from_member_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member not part of draw")

    anon = models.AnonymousMessage(
        group_id=group_id,
        from_member_id=payload.from_member_id,
        to_member_id=assignment.giver_id,
        direction="a",
        body=payload.answer,
    )
    session.add(anon)
    await session.commit()
    return schemas.AnonymousRelayResponse(status="ok")
