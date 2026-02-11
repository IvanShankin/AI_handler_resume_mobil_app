import asyncio

from src.modile.config import set_config
from src.modile.models.config_model import Config
from src.modile.ui.main_ui import AuthApp


async def main():
    async_loop = asyncio.new_event_loop()
    conf = Config(
        base_url = "http://localhost:8080",
        global_event_loop = async_loop
    )
    set_config(conf)
    AuthApp().run()


if __name__ == "__main__":
    asyncio.run(main())

