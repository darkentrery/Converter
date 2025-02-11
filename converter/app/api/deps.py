import typing as t

import fastapi

from app import service
from app.repository.sqlalchemy import SAUnitOfWork


class Pagination:
    def __init__(
        self, offset: int = fastapi.Query(0, ge=0), limit: int = fastapi.Query(20, le=100, gt=0)
    ):
        self.offset = offset
        self.limit = limit


def get_service(srv_class):
    def dep(request: fastapi.Request):
        uow = SAUnitOfWork(request.app.state.pg_async_session_maker)
        return srv_class(uow)

    return dep


# PaginationDep = t.Annotated[Pagination, fastapi.Depends(Pagination)]
# RackServiceDep = t.Annotated[service.RackService, fastapi.Depends(get_service(service.RackService))]

