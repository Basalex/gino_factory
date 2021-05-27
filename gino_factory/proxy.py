from functools import wraps
from typing import Iterable, Iterator, Optional, List

from faker import Faker
from gino.crud import CRUDModel

faker = Faker("en")


class BaseProxyFactory:
    def __init__(self, factory_cls, amount: int):
        self._factory_cls = factory_cls
        self.amount = amount

    @staticmethod
    def _process_kwargs(kwargs):
        attrs = kwargs.copy()
        for k, v in kwargs.items():
            if isinstance(v, Iterator):
                attrs[k] = next(v)
        return attrs


class ProxyFactory(BaseProxyFactory):
    def __getattr__(self, attr: str):
        attr = getattr(self._factory_cls, attr)
        if callable(attr):
            @wraps(attr)
            async def repeater(*args, _amount: int = self.amount, **kwargs):
                return [
                    await attr(*args, **ProxyFactory._process_kwargs(kwargs))
                    for _ in range(_amount)
                ]
            return repeater
        else:
            return attr


class ProxyTreeFactory(BaseProxyFactory):
    def __init__(
        self,
        factory_cls,
        amount: int,
        max_depth: Optional[int] = 5,
        top_parents_amount: Optional[int] = 3,
        top_parents: Optional[List[CRUDModel]] = None,
        parent_field_name: Optional[str] = "parent_id",
    ):
        super().__init__(factory_cls, amount)
        self.__max_depth__ = max_depth
        self.__parent_field_name__ = parent_field_name
        self.__top_parents_amount__ = top_parents_amount
        self.__top_parents__ = top_parents
        assert top_parents_amount < amount, "Parameter top_parents_amount cannot be greater then amount!"

    def __getattr__(self, attr: str):
        attr = getattr(self._factory_cls, attr)
        if hasattr(attr, "__call__"):

            @wraps(attr)
            async def tree_builder(*args, _amount: int = self.amount, **kwargs):
                if self.__top_parents__ is not None:
                    parents = [(parent, 0) for parent in self.__top_parents__]
                else:
                    parents = []
                    for _ in range(self.__top_parents_amount__):
                        parent = await attr(
                            *args,
                            **{self.__parent_field_name__: None},
                            **ProxyFactory._process_kwargs(kwargs),
                        )
                        parents.append((parent, 0))

                children, top_parents_amount = [], len(parents)
                for _ in range(self.amount - self.__top_parents_amount__):
                    parent, level = faker.random_element(parents)
                    element = await attr(
                        *args,
                        **{self.__parent_field_name__: parent},
                        **ProxyFactory._process_kwargs(kwargs),
                    )
                    if level < self.__max_depth__:
                        parents.append((element, level + 1))
                    else:
                        children.append(element)

                return [item for item, _ in parents] + children

            return tree_builder
        else:
            return attr
