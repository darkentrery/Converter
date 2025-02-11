import abc

import pydantic

AnyModel = dict[str, any]
Entity = pydantic.BaseModel
FindAllResult = tuple[int, list[Entity]]


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, data: AnyModel) -> Entity:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, filter_by: AnyModel):
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, id: int, data: AnyModel):
        raise NotImplementedError

    @abc.abstractmethod
    async def patch(self, id: int, data: AnyModel):
        raise NotImplementedError

    @abc.abstractmethod
    async def find_or_none(self, filter_by: AnyModel) -> Entity | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def find(self, filter_by: AnyModel) -> Entity:
        raise NotImplementedError

    @abc.abstractmethod
    async def find_all(self, filter_by: AnyModel, offset: int, limit: int, order: str = "desc") -> FindAllResult:
        raise NotImplementedError


class AbstractUnitOfWork(abc.ABC):
    outbox: AbstractRepository

    @abc.abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(self, *args):
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


__all__ = [
    'AnyModel',
    'FindAllResult',
    'AbstractRepository',
    'AbstractUnitOfWork'
]
