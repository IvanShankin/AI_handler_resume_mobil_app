import asyncio
import threading

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

from src.api_client.auth import AuthClient
from src.api_client.models import UserCreate
from src.modile.config import get_config
from src.modile.ui.creating_elements import create_textinput, create_button
from src.modile.view_models.auth_vm import AuthViewModel


class LoginScreen(Screen):
    def __init__(self, viewmodel: AuthViewModel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        # --- UI остаётся ---
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        layout = BoxLayout(orientation="vertical", spacing=15, size_hint=(0.8, None))
        layout.bind(minimum_height=layout.setter('height'))

        self.username_input = create_textinput("Email")
        self.password_input = create_textinput("Password", password=True)
        self.message_label = Label(size_hint=(1, None), height=30)

        login_btn = create_button("Вход")
        login_btn.bind(on_release=self.login_clicked)

        go_register_btn = create_button("Зарегистрироваться")
        go_register_btn.bind(on_release=self.go_to_register)

        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_btn)
        layout.add_widget(go_register_btn)
        layout.add_widget(self.message_label)

        anchor.add_widget(layout)
        self.add_widget(anchor)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def go_to_register(self, button):
        self.manager.current = "register"

    def login_clicked(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        conf = get_config()
        asyncio.run_coroutine_threadsafe(
            self._handle_login(username, password),
            conf.global_event_loop
        )

    async def _handle_login(self, username, password):
        success, result = await self.viewmodel.login(username, password)

        if success:
            msg = f"Успешный вход"
        else:
            msg = f"Ошибка: {result}"

        Clock.schedule_once(lambda dt: setattr(self.message_label, "text", msg))
