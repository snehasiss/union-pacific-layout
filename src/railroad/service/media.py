"""Curated, attributed representative media for asset records.

Entries deliberately live in the service adapter: media is presentation data,
not an operational property of a railroad asset.  Images are loaded on demand
at a modest thumbnail width and must include the source and licence needed for
attribution.
"""

from __future__ import annotations


MEDIA: dict[str, list[dict[str, str]]] = {
    "L124": [
        {
            "kind": "model",
            "title": "HO model photo — UP 3826",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L124-UP3826.png",
            "credit": "Layout owner",
        },
    ],
    "L125": [
        {
            "kind": "model",
            "title": "HO model photo — UP 3672",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L125-UP3672.png",
            "credit": "Layout owner",
        }
    ],
    "L127": [
        {
            "kind": "model",
            "title": "HO model photo — UP 3551",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L127-UP3551.png",
            "credit": "Layout owner",
        }
    ],
    "L128": [
        {
            "kind": "model",
            "title": "HO model photo — UP 5053",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L128-UP5053.png",
            "credit": "Layout owner",
        }
    ],
    "L129": [
        {
            "kind": "model",
            "title": "HO model photo — UP 9028",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L129-UP9028.png",
            "credit": "Layout owner",
        }
    ],
    "L132": [
        {
            "kind": "model",
            "title": "HO model photo — UP 7002",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L132-UP7002.png",
            "credit": "Layout owner",
        }
    ],
    "L135": [
        {
            "kind": "model",
            "title": "HO model photo — UP 2485",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L135-UP2485.png",
            "credit": "Layout owner",
        }
    ],
    "L136": [
        {
            "kind": "model",
            "title": "HO model photo — UP 604",
            "description": "Owner-supplied photo of the HO-scale model.",
            "url": "/static/img/models/L136-UP604.png",
            "credit": "Layout owner",
        }
    ],
}


def media_for(entity_id: str) -> list[dict[str, str]]:
    """Return presentation-media metadata for an existing asset ID."""
    return MEDIA.get(entity_id, [])
