from asyncio import AbstractEventLoop

from pydantic import BaseModel


class Config(BaseModel):
    base_url: str = "http://localhost:8080"
    global_event_loop: AbstractEventLoop

    model_config = {
        "arbitrary_types_allowed": True
    }