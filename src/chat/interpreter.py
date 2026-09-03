"""Interpret conversation as constrained asset-management intents."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from railroad.domain.identity import EntityType


@dataclass(frozen=True)
class Intent:
    operation: str
    query: str = ""
    entity_type: EntityType | None = None
    entity_id: str | None = None


class RuleInterpreter:
    """Predictable baseline used when no SLM is configured or available."""

    _TYPE_WORDS = {
        "locomotive": EntityType.LOCO,
        "locomotives": EntityType.LOCO,
        "loco": EntityType.LOCO,
        "locos": EntityType.LOCO,
        "car": EntityType.CAR,
        "cars": EntityType.CAR,
        "rolling stock": EntityType.CAR,
        "mow": EntityType.MOW,
        "maintenance of way": EntityType.MOW,
    }

    def interpret(self, message: str) -> Intent:
        text = " ".join(message.strip().split())
        lowered = text.casefold()
        entity_id = _entity_id(text)
        entity_type = next((value for word, value in self._TYPE_WORDS.items() if word in lowered), None)

        if re.search(r"\b(create|add|new)\b", lowered):
            return Intent("create", entity_type=entity_type)
        if re.search(r"\b(update|edit|change)\b", lowered):
            return Intent("update", entity_type=entity_type, entity_id=entity_id)
        if entity_id and re.fullmatch(r"(?:show|get|open|view)?\s*" + re.escape(entity_id), text, re.IGNORECASE):
            return Intent("detail", entity_id=entity_id)

        query = _query_from(text, lowered, entity_type)
        return Intent("search", query=query, entity_type=entity_type)


class SlmInterpreter:
    """Optional adapter for a local OpenAI-compatible SLM endpoint."""

    def __init__(self, url: str, model: str, fallback: RuleInterpreter | None = None) -> None:
        self.url = url.rstrip("/") + "/v1/chat/completions"
        self.model = model
        self.fallback = fallback or RuleInterpreter()

    def interpret(self, message: str) -> Intent:
        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 120,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Convert the asset-management request to one JSON object only. "
                        "Allowed operation: search, detail, create, update. Fields: operation, "
                        "query, entity_type (loco/car/mow/null), entity_id (or null). Never invent IDs."
                    ),
                },
                {"role": "user", "content": message},
            ],
        }
        try:
            body = json.dumps(payload).encode("utf-8")
            call = request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
            # Small models are quick once warm, but first-load CPU inference on
            # an Intel Mac can take longer than eight seconds.
            with request.urlopen(call, timeout=30) as response:
                result = json.load(response)
            content = result["choices"][0]["message"]["content"]
            return _intent_from_json(content)
        except (error.URLError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return self.fallback.interpret(message)


def interpreter_for(url: str | None, model: str):
    return SlmInterpreter(url, model) if url else RuleInterpreter()


def _intent_from_json(content: str) -> Intent:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise ValueError("SLM response did not contain JSON.")
    value: dict[str, Any] = json.loads(match.group(0))
    operation = value.get("operation")
    if operation not in {"search", "detail", "create", "update"}:
        raise ValueError("Unsupported SLM operation.")
    type_value = value.get("entity_type")
    return Intent(
        operation,
        query=str(value.get("query") or ""),
        entity_type=EntityType(type_value) if type_value else None,
        entity_id=value.get("entity_id"),
    )


def _entity_id(text: str) -> str | None:
    match = re.search(r"\b[LCM]\d{3}\b", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _query_from(text: str, lowered: str, entity_type: EntityType | None) -> str:
    patterns = (
        r"\broad\s+number\s+([\w-]+)",
        r"\bbuilt\s+by\s+(.+)$",
        r"\bmade\s+by\s+(.+)$",
        r"\b(?:find|search(?:\s+for)?|show(?:\s+me)?|list|get)\s+(.+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            query = match.group(1).strip(" .?")
            break
    else:
        query = text.strip(" .?")

    if entity_type:
        for word in RuleInterpreter._TYPE_WORDS:
            query = re.sub(rf"\b{re.escape(word)}\b", "", query, flags=re.IGNORECASE)
        query = re.sub(r"\b(with|all|the|roster)\b", "", query, flags=re.IGNORECASE)
        query = " ".join(query.split())
    if lowered in {"show roster", "show the roster", "list assets", "show assets"}:
        return ""
    return query
