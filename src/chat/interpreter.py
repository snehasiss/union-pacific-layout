"""Interpret conversation as constrained asset-management intents."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from railroad.domain.identity import EntityType
from railroad.domain.control import ControlType
from railroad.rs.car import CarType
from railroad.rs.loco import LocoType
from railroad.rs.mow import MOWType


@dataclass(frozen=True)
class Intent:
    operation: str
    query: str = ""
    entity_type: EntityType | None = None
    entity_id: str | None = None
    subtype: str | None = None
    control_type: ControlType | None = None
    sound: bool | None = None


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
        if list_intent := _list_intent(lowered):
            return list_intent
        entity_id = _entity_id(text)
        entity_type = next((value for word, value in self._TYPE_WORDS.items() if word in lowered), None)
        subtype = _subtype_from(lowered, entity_type)
        control_type, sound = _control_from(lowered)

        if re.search(r"\b(create|add|new)\b", lowered):
            return Intent("create", entity_type=entity_type, subtype=subtype, control_type=control_type, sound=sound)
        if re.search(r"\b(update|edit|change)\b", lowered):
            return Intent("update", entity_type=entity_type, entity_id=entity_id)
        if entity_id and re.fullmatch(r"(?:show|get|open|view)?\s*" + re.escape(entity_id), text, re.IGNORECASE):
            return Intent("detail", entity_id=entity_id)

        query = _query_from(text, lowered, entity_type)
        return Intent("search", query=query, entity_type=entity_type, subtype=subtype, control_type=control_type, sound=sound)


class SlmInterpreter:
    """Optional adapter for a local OpenAI-compatible SLM endpoint."""

    def __init__(self, url: str, model: str, fallback: RuleInterpreter | None = None) -> None:
        self.url = url.rstrip("/") + "/v1/chat/completions"
        self.model = model
        self.fallback = fallback or RuleInterpreter()
        self.debug_info: dict[str, Any] = {"source": "slm", "model": model}

    def interpret(self, message: str) -> Intent:
        # Exhaustive roster requests have an exact domain meaning. Keeping
        # them deterministic prevents a small model from inventing filters.
        if list_intent := _list_intent(" ".join(message.strip().casefold().split())):
            self.debug_info = {"source": "rules", "reason": "deterministic list command"}
            return list_intent
        control_type, sound = _control_from(message.casefold())
        if control_type is not None or sound is not None:
            intent = self.fallback.interpret(message)
            self.debug_info = {"source": "rules", "reason": "deterministic control filter"}
            return intent
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
                        "query, entity_type (loco/car/mow/null), subtype, control_type "
                        "(dc/dcc/unpowered/null), sound (true/false/null), entity_id (or null). "
                        "Subtype is steam/diesel/turbine for locomotives, a car type for cars, "
                        "or a MOW type. Put maker/builder text in query. Never invent IDs."
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
            intent = _intent_from_json(content)
            detected_subtype = _subtype_from(message.casefold(), intent.entity_type)
            if detected_subtype and not intent.subtype:
                intent = Intent(intent.operation, intent.query, intent.entity_type, intent.entity_id, detected_subtype)
            self.debug_info = {"source": "slm", "model": self.model, "raw_response": content}
            return intent
        except (error.URLError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            intent = self.fallback.interpret(message)
            self.debug_info = {
                "source": "rules-fallback",
                "model": self.model,
                "raw_response": locals().get("content"),
                "reason": f"{type(exc).__name__}: {exc}",
            }
            return intent


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
    entity_type = EntityType(type_value) if type_value else None
    subtype = str(value.get("subtype") or "").casefold() or None
    if subtype and (entity_type is None or subtype not in _SUBTYPES[entity_type]):
        raise ValueError("Unsupported equipment subtype.")
    control_value = str(value.get("control_type") or "").casefold() or None
    control_type = ControlType(control_value) if control_value else None
    sound_value = value.get("sound")
    if sound_value is not None and not isinstance(sound_value, bool):
        raise ValueError("sound must be true, false, or null.")
    return Intent(
        operation,
        query=str(value.get("query") or ""),
        entity_type=entity_type,
        entity_id=value.get("entity_id"),
        subtype=subtype,
        control_type=control_type,
        sound=sound_value,
    )


def _entity_id(text: str) -> str | None:
    match = re.search(r"\b[LCM]\d{3}\b", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


_SUBTYPES = {
    EntityType.LOCO: {item.value for item in LocoType},
    EntityType.CAR: {item.value for item in CarType},
    EntityType.MOW: {item.value for item in MOWType},
}


def _subtype_from(text: str, entity_type: EntityType | None) -> str | None:
    if entity_type is None:
        return None
    return next(
        (subtype for subtype in _SUBTYPES[entity_type] if re.search(rf"\b{re.escape(subtype)}\b", text)),
        None,
    )


def _control_from(text: str) -> tuple[ControlType | None, bool | None]:
    control_type = None
    if re.search(r"\bdcc\b", text):
        control_type = ControlType.DCC
    elif re.search(r"\bdc\b", text):
        control_type = ControlType.DC
    elif re.search(r"\bunpowered\b", text):
        control_type = ControlType.UNPOWERED
    sound = True if re.search(r"\bsound\b", text) else None
    return control_type, sound


def _list_intent(text: str) -> Intent | None:
    normalized = text.strip(" .?!")
    match = re.fullmatch(
        r"(?:show|list|get|display)(?: me)?(?: all| the)? "
        r"(locomotives?|locos?|cars?|rolling stock|mow|maintenance of way|"
        r"assets?|equipments?|roster)",
        normalized,
    )
    if not match:
        return None
    target = match.group(1)
    entity_type = next(
        (value for word, value in RuleInterpreter._TYPE_WORDS.items() if word == target),
        None,
    )
    return Intent("search", entity_type=entity_type)


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
        query = re.sub(r"\b(dcc|dc|unpowered|sound)\b", "", query, flags=re.IGNORECASE)
        query = " ".join(query.split())
    if lowered in {"show roster", "show the roster", "list assets", "show assets"}:
        return ""
    return query
