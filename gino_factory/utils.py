import re
from typing import Type, Optional

import sqlalchemy as sa
from gino import json_support
from gino.crud import CRUDModel


def lazy_method(attr, factory_cls, **kwargs):
    return getattr(factory_cls, attr)(**kwargs)


def camel_to_snake_case(words: str):
    return re.sub("([A-Z][a-z]+)", r"\1_", words).rstrip("_").lower()


def get_model_fields(model: Type[CRUDModel]):
    fields = {
        field_name: getattr(model, field_name)
        for field_name in model._column_name_map.keys()
    }
    for key, prop in model.__dict__.items():
        if isinstance(prop, json_support.JSONProperty):
            fields[key] = getattr(model, key)
            fields.pop(prop.prop_name, None)
    return fields


async def get_or_create(model: CRUDModel, *, defaults: Optional[dict] = None, **kwargs):
    where_args = (
        getattr(model, key).is_(val) if isinstance(val, bool) else getattr(model, key) == val
        for key, val in kwargs.items()
    )
    obj = await model.query.where(sa.and_(*where_args)).gino.load(model).one_or_none()
    if obj is None:
        obj = await model.create(**kwargs, **(defaults or {}))
    return obj
