#!/usr/bin/env python3
# test_ops.py

import pytest

from railroad.domain.identity import EntityType
from railroad.operation.ops import resolve_type, validate_id


def test_validate_id():
    assert validate_id("L001") == "L001"


def test_validate_id_rejects_bad_id():
    with pytest.raises(ValueError):
        validate_id("L1")


@pytest.mark.parametrize(
    ("entity_id", "entity_type"),
    [
        ("L001", EntityType.LOCO),
        ("C001", EntityType.CAR),
        ("M001", EntityType.MOW),
        ("G001", EntityType.SIGNAL),
        ("T001", EntityType.TURNOUT),
    ],
)
def test_resolve_type(entity_id, entity_type):
    assert resolve_type(entity_id) == entity_type
