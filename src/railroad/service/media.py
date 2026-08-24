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
            "title": "Union Pacific Challenger 3985",
            "description": "Representative 4-6-6-4 Challenger prototype image; not the model itself.",
            "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Union_Pacific_No._3985_%22Challenger%22_%28September_28%2C_2008%29_%282903858658%29.jpg?width=640",
            "source_url": "https://commons.wikimedia.org/wiki/File:Union_Pacific_No._3985_%22Challenger%22_(September_28,_2008)_(2903858658).jpg",
            "credit": "Michael Hicks",
            "license": "CC BY 2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
        }
    ]
}


def media_for(entity_id: str) -> list[dict[str, str]]:
    """Return presentation-media metadata for an existing asset ID."""
    return MEDIA.get(entity_id, [])
