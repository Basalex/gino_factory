from collections import UserDict
from datetime import date, datetime, time
from functools import partial
from typing import Optional

from faker import Faker

faker = Faker("en")
faker_float = partial(
    faker.pyfloat, min_value=1000, max_value=20000, right_digits=2, positive=True
)


def random_string(max_length: Optional[int] = 5):
    return faker.word()[:max_length or 10]


class FactoryDict(UserDict):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError as e:
            for k, v in self.data.items():
                try:
                    if k == item:
                        return v
                except TypeError:
                    return None
            raise e from None


class contains:
    def __init__(self, *strings: str):
        self.strings = tuple(strings)

    def __hash__(self):
        return hash(self.strings)

    def __eq__(self, other):
        return all(string in other for string in self.strings)

    def __repr__(self):
        strings = ", ".join(self.strings)
        return f'contains["{strings}"]'


factory_dict = FactoryDict(
    {
        contains("username"): faker.user_name,
        # contains("email"): faker.email,
        contains("phone"): faker.phone_number,
        contains("password"): faker.password,
        contains("first", "name"): faker.first_name,
        contains("last", "name"): faker.last_name,
        contains("file", "name"): faker.file_name,
        contains("name"): faker.name,
        contains("birth", "date"): faker.date_of_birth,
        contains("url"): faker.url,
        contains("slug"): faker.slug,
        float: faker_float,
        bool: faker.boolean,
        int: faker.pyint,
        datetime: faker.date_time,
        date: lambda: faker.date_time().date(),
        time: lambda: faker.date_time().time(),
    }
)

factory_dict_with_args = FactoryDict(
    {
        str: (random_string, {"max_length": lambda field: field.type.length}),
    }
)
