from __future__ import annotations

import random
import uuid
from typing import Dict, Iterable, List, Sequence, Set


class PairingError(Exception):
    pass


def make_assignments(
    members: Sequence[dict],
    exclusions: Dict[uuid.UUID, Set[uuid.UUID]],
    allow_household: bool = False,
    seed: int | None = None,
) -> Dict[uuid.UUID, uuid.UUID]:
    rng = random.Random(seed)
    receivers = list(members)
    assignment: Dict[uuid.UUID, uuid.UUID] = {}

    def can_give(giver: dict, receiver: dict) -> bool:
        if giver["id"] == receiver["id"]:
            return False
        if not allow_household and giver.get("household") and giver.get("household") == receiver.get("household"):
            return False
        if receiver["id"] in exclusions.get(giver["id"], set()):
            return False
        return True

    givers = sorted(members, key=lambda m: len(exclusions.get(m["id"], [])), reverse=True)

    def backtrack(index: int, available_receivers: List[dict]) -> bool:
        if index == len(givers):
            return True
        giver = givers[index]
        candidates = [r for r in available_receivers if can_give(giver, r)]
        rng.shuffle(candidates)
        for receiver in candidates:
            assignment[giver["id"]] = receiver["id"]
            remaining = [r for r in available_receivers if r["id"] != receiver["id"]]
            if backtrack(index + 1, remaining):
                return True
            assignment.pop(giver["id"], None)
        return False

    if not backtrack(0, receivers):
        raise PairingError("No valid pairing found.")
    return assignment
