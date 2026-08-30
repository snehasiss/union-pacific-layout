from __future__ import annotations

import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = SOURCE_ROOT.parent
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from railroad.config import Config  # noqa: E402
from railroad.domain.control import ControlType  # noqa: E402
from railroad.domain.identity import EntityType  # noqa: E402
from railroad.domain.model import Status  # noqa: E402
from railroad.operation import Roster  # noqa: E402

OPERABLE_STATUSES = {Status.ACTIVE}


def available_locomotives() -> list[dict[str, object]]:
    """Return physically available DCC locomotives using the shared operation API."""
    config = Config(REPOSITORY_ROOT / "config" / "railroad-conf.json")
    roster = Roster.from_config(config, (EntityType.LOCO,))
    locomotives = [
        {
            "id": locomotive.id,
            "reportingMark": locomotive.reporting_mark,
            "roadNumber": locomotive.road_number,
            "railroad": locomotive.railroad,
            "prototype": locomotive.prototype_model,
            "nickname": locomotive.nickname,
            "status": locomotive.model.status.value,
            "address": locomotive.control.address,
            "light": locomotive.control.light,
            "sound": locomotive.control.sound,
            "smoke": locomotive.control.smoke,
        }
        for locomotive in roster
        if locomotive.model.status in OPERABLE_STATUSES
        and locomotive.control.type == ControlType.DCC
        and locomotive.control.address is not None
    ]
    return sorted(
        locomotives,
        key=lambda item: (str(item["reportingMark"]), str(item["roadNumber"]), str(item["id"])),
    )
