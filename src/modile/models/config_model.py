from asyncio import AbstractEventLoop
from pathlib import Path

from pydantic import BaseModel

from src.modile.utils.token_storage import TokenStorage


class Config(BaseModel):
    base_url: str = "http://localhost:8080"

    max_char_requirements: int = 1000
    max_char_resume: int = 5000

    base: Path = Path(__file__).resolve().parents[3]
    media: Path = base / Path("media")
    log_file: Path = media / Path("mobile_app.log")

    global_event_loop: AbstractEventLoop
    token_storage: TokenStorage = TokenStorage()

    model_config = {
        "arbitrary_types_allowed": True,
    }