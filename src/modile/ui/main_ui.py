import asyncio
import threading

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from src.api_client.auth import AuthClient
from src.modile.config import get_config
from src.modile.ui.screens.auth.login import LoginScreen
from src.modile.ui.screens.auth.register import RegisterScreen
from src.modile.utils.event_loop import start_loop
from src.modile.view_models.auth_vm import AuthViewModel, RegViewModel


class RootScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # белый фон
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos


class AuthApp(App):
    def build(self):
        conf = get_config()
        self.loop = asyncio.get_event_loop()
        self.auth_client = AuthClient(conf.base_url)

        sm = RootScreenManager(
            transition=FadeTransition(duration=0.15)
        )
        sm.add_widget(LoginScreen(name="login", viewmodel=AuthViewModel(auth_client=self.auth_client)))
        sm.add_widget(RegisterScreen(name="register", viewmodel=RegViewModel(auth_client=self.auth_client)))

        # Запускаем глобальный event loop в отдельном потоке
        t = threading.Thread(target=start_loop, args=(conf.global_event_loop,), daemon=True)
        t.start()

        return sm

    def on_stop(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.auth_client.close())
