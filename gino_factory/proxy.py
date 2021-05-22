from functools import wraps
from typing import Iterable, Iterator, Optional

from faker import Faker

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
        max_depth: Optional[int] = None,
        single_tree: Optional[bool] = False,
        parent_field_name: Optional[str] = "parent_id",
    ):
        super().__init__(factory_cls, amount)
        self.__max_depth__ = max_depth
        self.__single_tree__ = single_tree
        self.__parent_field_name__ = parent_field_name

    def __getattr__(self, attr: str):
        attr = getattr(self._factory_cls, attr)
        if hasattr(attr, "__call__"):

            @wraps(attr)
            async def tree_builder(*args, _amount: int = self.amount, **kwargs):
                parents = kwargs.pop("parent", None)
                if isinstance(parents, Iterable):
                    parents = [(parent, 0) for parent in parents]
                else:
                    parents = [(parents, 0)]

                children, top_parents_amount = [], len(parents)
                for _ in range(self.amount):
                    parent, level = faker.random_element(
                        self.__single_tree__ and parents[top_parents_amount:] or parents
                    )
                    element = await attr(
                        *args, **{self.__parent_field_name__: parent}, **ProxyFactory._process_kwargs(kwargs)
                    )
                    if level < self.__max_depth__:
                        parents.append((element, level + 1))
                    else:
                        children.append(element)

                return [item for item, _ in parents[top_parents_amount:]] + children

            return tree_builder
        else:
            return attr
