from asyncio import AbstractEventLoop
from pathlib import Path

from kivy.app import App
from pydantic import BaseModel

from src.mobile.utils.token_storage import TokenStorage

def get_base_dir() -> Path:
    try:
        app = App.get_running_app()
        if app:
            return Path(app.user_data_dir)
    except Exception:
        pass

    # fallback для dev режима
    return Path(__file__).resolve().parents[3]


class Config(BaseModel):
    base_url: str = "http://localhost:8080"

    max_char_requirements: int = 1000
    max_char_resume: int = 5000

    bg_color: tuple[float, float, float, float] = (0.92, 0.92, 0.92, 1)
    panel_color: tuple[float, float, float, float] = (0.92, 0.92, 0.92, 1)
    card_color: tuple[float, float, float, float] = (1, 1, 1, 1)
    text_color: tuple[float, float, float, float] = (0.14, 0.14, 0.16, 1)
    subtle_text_color: tuple[float, float, float, float] = (0.35, 0.35, 0.38, 1)
    btn_neutral_bg: tuple[float, float, float, float] = (2.2, 2.2, 2.2, 1)
    btn_neutral_bg_soft: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1)
    btn_primary_bg: tuple[float, float, float, float] = (0.28, 0.28, 0.31, 1)
    btn_danger_bg: tuple[float, float, float, float] = (0.4, 0.4, 0.43, 1)
    fab_bg: tuple[float, float, float, float] = (0.2, 0.2, 0.22, 1)

    base: Path = get_base_dir()
    media: Path = base / Path("media")
    log_file: Path = media / Path("mobile_app.log")
    copy_icon: Path = media / Path("copy_icon.png")

    global_event_loop: AbstractEventLoop
    token_storage: TokenStorage = TokenStorage()

    class Config:
        arbitrary_types_allowed = True
