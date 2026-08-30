"""Load curated presentation media without adding it to the domain model."""

from __future__ import annotations

import json
import re
from pathlib import Path

from railroad.config import Config


def _manifest_paths(config: Config) -> tuple[Path, ...]:
    """Return the service media manifests, grouped beside their asset data."""
    return (
        config.data_config("loco").path / "loco-media.json",
        config.data_config("mow").path / "mow-media.json",
    )


def _filename(config: Config, asset_id: str, index: int, identities: dict[str, tuple[str, str]]) -> str:
    """Build a stable, human-readable optimized-media filename."""
    if asset_id not in identities:
        data_name = {"L": "loco", "M": "mow"}[asset_id[0]]
        payload = json.loads((config.data_config(data_name).path / f"{asset_id}.json").read_text(encoding="utf-8"))
        identity = payload["identity"]
        identities[asset_id] = identity["reporting_mark"], identity["road_number"]
    reporting_mark, road_number = identities[asset_id]
    mark_and_number = re.sub(r"[^A-Za-z0-9]+", "", f"{reporting_mark}{road_number}").upper()
    return f"{asset_id}-{mark_and_number}-{index}.jpg"


def _local(photo: list[str], copyright: str, filename: str) -> tuple[str, dict[str, str]]:
    asset_id, kind, title, *_ = photo
    description = (
        "Owner-supplied photograph of the full-size locomotive."
        if kind == "prototype"
        else "Owner-supplied photograph of the HO-scale model."
    )
    return asset_id, {
        "kind": kind,
        "title": title,
        "description": description,
        "url": f"/photos/{filename}",
        "credit": copyright,
    }


def _flickr(photo: list[str | None], copyright: str, filename: str) -> tuple[str, dict[str, str]]:
    asset_id, photo_id, album_id, title = photo
    source_url = f"https://www.flickr.com/photos/iconic/{photo_id}/"
    if album_id:
        source_url += f"in/album-{album_id}/"
    return asset_id, {
        "kind": "model",
        "title": f"HO model photo — {title}",
        "description": "Owner-supplied photograph imported from the layout owner's Flickr collection.",
        "url": f"/photos/{filename}",
        "credit": copyright,
        "source_url": source_url,
    }


def media_for(config: Config, entity_id: str) -> list[dict[str, str]]:
    """Return the configured presentation media for an existing asset ID.

    The manifest deliberately lives beside locomotive data, but remains a
    service concern rather than an attribute of a locomotive domain object.
    """
    media: dict[str, list[dict[str, str]]] = {}
    identities: dict[str, tuple[str, str]] = {}
    for path in _manifest_paths(config):
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        copyright = payload["copyright"]
        photos = (("local", photo) for photo in payload.get("local_photos", []))
        photos = (*photos, *(("flickr", photo) for photo in payload.get("flickr_photos", [])))
        counts: dict[str, int] = {}
        for kind, photo in photos:
            asset_id = photo[0]
            counts[asset_id] = counts.get(asset_id, 0) + 1
            filename = _filename(config, asset_id, counts[asset_id], identities)
            factory = _local if kind == "local" else _flickr
            asset_id, item = factory(photo, copyright, filename)
            media.setdefault(asset_id, []).append(item)
    return media.get(entity_id, [])
