import io
from typing import Callable

from httpx import AsyncClient, Response
from pydantic import TypeAdapter

from app import entity, exc
from app.config import config


class ApiService:
    def __init__(self, api_client: AsyncClient):
        self.api_client = api_client
        self.host = config.api_host + "/converter/v1"

    async def get_formats(self) -> list[entity.Format]:
        res = await self.get("/formats/")
        return TypeAdapter(list[entity.Format]).validate_python(res.json())

    async def get_formats_with_pair(self) -> list[entity.Format]:
        res = await self.get("/formats/with-pair/")
        return TypeAdapter(list[entity.Format]).validate_python(res.json())

    async def get_cross_formats_by_format_name(self, format_name: str) -> list[entity.FormatCrossWithName]:
        res = await self.get(f"/formats/{format_name}/cross/")
        return TypeAdapter(list[entity.FormatCrossWithName]).validate_python(res.json())

    async def convert(self, format_from: str, format_to: str, body: dict) -> bytes:
        res = await self.post(f"/converters/from-{format_from}-to-{format_to}", body)
        file_bytes = io.BytesIO(res.read())
        file_bytes.seek(0)
        return file_bytes.getvalue()

    async def get_user_by_tg_id(self, tg_id: int) -> entity.User:
        res = await self.get(f"/users/by-tg/{tg_id}")
        return TypeAdapter(entity.User).validate_python(res.json())

    async def create_user(self, body: entity.AddUser) -> entity.User:
        res = await self.post("/users/", body.model_dump())
        return TypeAdapter(entity.User).validate_python(res.json())

    async def create_user_action(self, body: entity.AddUserAction) -> entity.UserAction:
        res = await self.post("/user-actions/", body.model_dump())
        return TypeAdapter(entity.UserAction).validate_python(res.json())

    async def create_feedback(self, body: entity.AddFeedback) -> entity.Feedback:
        res = await self.post("/feedbacks/", body.model_dump())
        return TypeAdapter(entity.Feedback).validate_python(res.json())

    async def get_statistic(self) -> entity.Statistic:
        res = await self.get("/user-actions/statistic")
        return TypeAdapter(entity.Statistic).validate_python(res.json())

    def call_api(method: Callable):
        async def wrapper(self, *args, **kwargs) -> Response:
            res: Response = await method(self, *args, **kwargs)
            match res.status_code:
                case 200 | 201 | 204:
                    return res
                case 404:
                    raise exc.NotFoundError
                case 409:
                    raise exc.AlreadyExists
                case _:
                    raise exc.InvalidRequest

        return wrapper

    @call_api
    async def post(self, url: str, body: dict) -> Response:
        res = await self.api_client.post(
            self.host + url,
            json=body
        )
        return res

    @call_api
    async def get(self, url: str) -> Response:
        res = await self.api_client.get(
            self.host + url,
        )
        return res
