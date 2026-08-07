#!/usr/bin/env python3

# dataclassfactory.py

from dataclasses import fields
from datetime import datetime, date
from typing import Any, Union, get_args, get_origin


class DataclassFactory:

    @classmethod
    def build(cls, dataclass_type, data: dict):
        """
        Construct any dataclass from a dictionary.

        Extra keys are ignored.
        Missing keys become None (or the dataclass default).
        Type conversion is automatic.
        """

        values = {}

        for field in fields(dataclass_type):

            name = field.name
            field_type = cls._resolve_type(field.type)

            if name not in data:
                continue

            values[name] = cls._convert(
                data[name],
                field_type
            )

        return dataclass_type(**values)

    #################################################################
    # Internal helper methods
    #################################################################

    @staticmethod
    def _resolve_type(field_type):
        """
        Converts Optional[int] -> int
                 Optional[str] -> str
        """

        origin = get_origin(field_type)

        if origin is Union:
            args = [
                arg
                for arg in get_args(field_type)
                if arg is not type(None)
            ]

            if len(args) == 1:
                return args[0]

        return field_type

    @staticmethod
    def _convert(value: Any, target_type):

        if value is None:
            return None

        if isinstance(value, str):

            value = value.strip()

            if value == "":
                return None

        try:

            if target_type is bool:

                return str(value).lower() in (
                    "y",
                    "yes",
                    "true",
                    "1"
                )

            if target_type is int:

                return int(value)

            if target_type is float:

                return float(value)

            if target_type is date:

                return datetime.strptime(
                    value,
                    "%d-%b-%Y"
                ).date()

            return target_type(value)

        except Exception:

            #
            # If conversion fails,
            # simply return original value.
            #
            return value


