from asyncio import AbstractEventLoop

from pydantic import BaseModel

from src.modile.utils.token_storage import TokenStorage


class Config(BaseModel):
    base_url: str = "http://localhost:8080"
    global_event_loop: AbstractEventLoop
    token_storage: TokenStorage = TokenStorage()

    model_config = {
        "arbitrary_types_allowed": True
    }