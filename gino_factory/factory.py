import asyncio
import enum
import random
from collections import namedtuple
from functools import partial
from typing import Any, Mapping, Iterator, Iterable, Optional, Type, Union

from gino.crud import CRUDModel

from gino_factory.faker import factory_dict, factory_dict_with_args, faker
from gino_factory.proxy import ProxyFactory, ProxyTreeFactory
from gino_factory.utils import camel_to_snake_case, get_model_fields, lazy_method


PyiType = namedtuple("PyiType", ["class_name", "base", "type_wrapper"])


class GinoFactoryMeta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        namespace.setdefault("_factory_models", {})
        namespace.setdefault("_annotations", {})
        namespace.setdefault("_models_name_mapping", {})
        namespace.setdefault("_models_table_mapping", {})
        return super().__new__(mcs, name, bases, namespace)

    def __getattr__(self, attr: str):
        model = self._models_name_mapping[attr]
        factory_model = self._factory_models[attr]
        return partial(self.__create_object__, model, **factory_model)


class GinoFactory(metaclass=GinoFactoryMeta):
    _factory_dict = factory_dict
    _factory_dict_with_args = factory_dict_with_args
    _proxy_cls = ProxyFactory
    _proxy_tree_cls = ProxyTreeFactory

    @classmethod
    def _get_factory_by_type(cls, field, python_type):
        factory = cls._factory_dict.get(python_type)
        if factory is None:
            factory = cls._factory_dict_with_args.get(python_type)
            if factory is not None:
                factory, args = factory
                factory = partial(factory, **{k: v(field) for k, v in args.items()})
            else:
                if issubclass(python_type, enum.Enum):
                    factory = lambda enum_type=python_type: faker.random_element(enum_type)  # noqa: E731
                elif issubclass(python_type, Mapping):
                    factory = lambda: {}
                elif issubclass(python_type, Iterable):
                    inner_type = field.type.item_type.python_type
                    pre_factory = cls._get_factory_by_type(field, inner_type)
                    factory = lambda: python_type(pre_factory() for _ in range(random.randint(1, 100)))
        return factory

    @classmethod
    def register(cls, __model__: Type[CRUDModel], __name__: Optional[str] = None, **field_factories):
        model = __model__
        model_factory = {}
        annotations = {}
        method_name = __name__ or camel_to_snake_case(model.__name__)
        cls._models_name_mapping[method_name] = model
        cls._models_table_mapping[model.__table__.name] = model
        for field_name, field in get_model_fields(model).items():
            try:
                python_type = field.type.python_type
            except NotImplementedError:
                python_type = str
            if field_name not in field_factories and field.foreign_keys:
                column = list(field.foreign_keys)[0].column
                table_name = column.table.name
                try:
                    fk_model = cls._models_table_mapping[table_name]
                except KeyError:
                    raise ValueError(
                        f"{model.__name__.title()} factory requires method for Model with table name '{table_name}'"
                        " to be defined!"
                    )
                if fk_model is not model:
                    fk_name = camel_to_snake_case(fk_model.__name__)
                    model_factory[field_name] = partial(lazy_method, fk_name, cls)
                    annotations[field_name] = python_type
            elif not hasattr(field, "autoincrement") or field.autoincrement is not True:
                try:
                    factory = field_factories.pop(field_name)
                except KeyError:
                    factory = cls._factory_dict.get(field_name) or cls._factory_dict_with_args.get(field_name)
                    if factory is None:
                        factory = cls._get_factory_by_type(field, python_type)
                        if factory is None:
                            if issubclass(python_type, enum.Enum):
                                factory = lambda enum_type=python_type: faker.random_element(enum_type)  # noqa: E731
                            elif issubclass(python_type, Iterable):
                                python_type = field.type.item_type
                            elif hasattr(field, "server_default") and not field.server_default and not field.default:
                                raise ValueError(
                                    f"{field_name} is required, was not able to find factory function!"
                                )
                model_factory[field_name] = factory
                annotations[field_name] = python_type

        if field_factories:
            attrs = ", ".join(field_factories.keys())
            raise ValueError(
                f"{model.__name__.title()} model hasn`t got attributes: {attrs}"
            )
        cls._factory_models[method_name] = model_factory
        cls._annotations[method_name] = annotations

    @classmethod
    def cycle(cls, amount: Optional[int] = None) -> Union["GinoFactory", "ProxyFactory", Any]:
        return cls._proxy_cls(cls, amount)

    @classmethod
    def tree(
        cls, amount: int = 50, max_depth: int = 5, single_tree: bool = False,
    ) -> Union["GinoFactory", "ProxyTreeFactory", Any]:
        return cls._proxy_tree_cls(
            cls,
            amount,
            max_depth=max_depth,
            single_tree=single_tree,
        )

    @classmethod
    async def __create_object__(cls, model, /, **kwargs):
        obj_data = {}
        for key, item in kwargs.items():
            if isinstance(item, Iterator):
                item = next(item)
            if callable(item):
                item = item()
                if asyncio.iscoroutine(item):
                    item = await item
            if isinstance(item, CRUDModel):
                for fk in getattr(model, key).foreign_keys:
                    if fk.column.table.name == item.__table__.name:
                        item = getattr(item, fk.column.name)
                        break
            obj_data[key] = item
        return await model.create(**obj_data)

    @classmethod
    async def __random__(cls):
        for method_name in cls._factory_models.keys():
            proxy = cls.cycle(amount=random.randint(1, 30))
            await (getattr(proxy, method_name)())
