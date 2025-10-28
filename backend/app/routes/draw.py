from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..db import get_session
from ..services.pairing import PairingError, make_assignments
from ..services.security import get_current_group_id
from ..tasks.mail_tasks import send_assignment_email

router = APIRouter(prefix="/groups", tags=["draw"])


@router.post("/{group_id}/draw", response_model=schemas.DrawResponse)
async def trigger_draw(
    group_id: uuid.UUID,
    current_group_id: uuid.UUID = Depends(get_current_group_id),
    session: AsyncSession = Depends(get_session),
):
    if current_group_id != group_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    result = await session.execute(
        select(models.Group).where(models.Group.id == group_id).options()
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    members_result = await session.execute(
        select(models.Member).where(models.Member.group_id == group_id)
    )
    members = members_result.scalars().all()
    if len(members) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough members")

    exclusions_result = await session.execute(
        select(models.Exclusion).where(models.Exclusion.group_id == group_id)
    )
    exclusions = {}
    for exclusion in exclusions_result.scalars().all():
        exclusions.setdefault(exclusion.member_id, set()).add(exclusion.excluded_member_id)

    member_dicts = [
        {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "household": member.household,
            "interests": member.interests or [],
            "nogos": member.nogos or [],
        }
        for member in members
    ]

    try:
        assignment_map = make_assignments(
            member_dicts,
            exclusions,
            allow_household=group.allow_household,
        )
    except PairingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await session.execute(
        models.Assignment.__table__.delete().where(models.Assignment.group_id == group_id)
    )
    assignments = [
        models.Assignment(
            group_id=group_id,
            giver_id=giver_id,
            receiver_id=receiver_id,
        )
        for giver_id, receiver_id in assignment_map.items()
    ]
    session.add_all(assignments)
    await session.commit()

    member_lookup = {member.id: member for member in members}
    for giver_id, receiver_id in assignment_map.items():
        giver = member_lookup[giver_id]
        receiver = member_lookup[receiver_id]
        context = {
            "receiver_name": receiver.name,
            "budget": group.budget,
            "interests": receiver.interests or [],
            "nogos": receiver.nogos or [],
            "group_name": group.name,
        }
        send_assignment_email.delay(
            to_email=giver.email,
            subject=f"Secret Santa assignment for {group.name}",
            context=context,
        )

    return schemas.DrawResponse(status="ok", assigned=len(assignments))
