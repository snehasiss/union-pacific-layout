"""Load curated presentation media without adding it to the domain model."""

from __future__ import annotations

import json
from pathlib import Path

from railroad.config import Config


def _manifest_path(config: Config) -> Path:
    """Return the locomotive media manifest path."""
    return config.data_config("loco").path / "loco-media.json"


def _local(asset_id: str, kind: str, title: str, copyright: str) -> tuple[str, dict[str, str]]:
    description = (
        "Owner-supplied photograph of the full-size locomotive."
        if kind == "prototype"
        else "Owner-supplied photograph of the HO-scale model."
    )
    return asset_id, {
        "kind": kind,
        "title": title,
        "description": description,
        "url": f"/static/img/media/{asset_id}-{kind}-local.jpg",
        "credit": copyright,
    }


def _flickr(asset_id: str, photo_id: str, album_id: str | None, title: str, copyright: str) -> tuple[str, dict[str, str]]:
    source_url = f"https://www.flickr.com/photos/iconic/{photo_id}/"
    if album_id:
        source_url += f"in/album-{album_id}/"
    return asset_id, {
        "kind": "model",
        "title": f"HO model photo — {title}",
        "description": "Owner-supplied photograph imported from the layout owner's Flickr collection.",
        "url": f"/static/img/media/flickr-{photo_id}.jpg",
        "credit": copyright,
        "source_url": source_url,
    }


def media_for(config: Config, entity_id: str) -> list[dict[str, str]]:
    """Return the configured presentation media for an existing asset ID.

    The manifest deliberately lives beside locomotive data, but remains a
    service concern rather than an attribute of a locomotive domain object.
    """
    path = _manifest_path(config)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    copyright = payload["copyright"]
    media: dict[str, list[dict[str, str]]] = {}
    for photo in payload.get("local_photos", []):
        asset_id, item = _local(*photo, copyright)
        media.setdefault(asset_id, []).append(item)
    for photo in payload.get("flickr_photos", []):
        asset_id, item = _flickr(*photo, copyright)
        media.setdefault(asset_id, []).append(item)
    return media.get(entity_id, [])
