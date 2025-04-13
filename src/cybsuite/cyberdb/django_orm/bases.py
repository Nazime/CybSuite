import abc
from typing import Generic, Iterable, TypeVar

from koalak.descriptions import SchemaDescription

T = TypeVar("T")


class AbstractDatabase(abc.ABC):
    schema: SchemaDescription

    def __init__(
        self,
        name: str,
        *,
        host=None,
        port=None,
        user=None,
        password=None,
    ):
        if host is None:
            host = "127.0.0.1"
        self.name = name
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @abc.abstractmethod
    def __getitem__(self, item: str) -> "AbstractContainer":
        pass

    def __iter__(self) -> Iterable["AbstractContainer"]:
        for entity in self.schema:
            yield self[entity.name]


class AbstractContainer(Generic[T], abc.ABC):
    @abc.abstractmethod
    def feed(self):
        pass

    @abc.abstractmethod
    def count(self) -> int:
        pass


class AbstractDatabaseBuilder:
    def build(self, schema: SchemaDescription) -> "AbstractDatabase":
        pass
