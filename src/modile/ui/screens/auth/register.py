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
from src.modile.view_models.auth_vm import RegViewModel


class RegisterScreen(Screen):
    def __init__(self, viewmodel: RegViewModel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # светло-серый
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')

        layout = BoxLayout(orientation="vertical", spacing=15, size_hint=(0.8, None))
        layout.bind(minimum_height=layout.setter('height'))

        self.email_input = create_textinput("Email")
        self.password_input = create_textinput("Password", password=True)
        self.fullname_input = create_textinput("Full Name")
        self.message_label = Label(size_hint=(1, None), height=30, color=(1,0,0,1))

        register_btn = create_button("Зарегистрироваться")
        register_btn.bind(on_release=self.register)

        go_login_btn = create_button("Ко входу")
        go_login_btn.bind(on_release=self.go_to_login)

        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.fullname_input)
        layout.add_widget(register_btn)
        layout.add_widget(go_login_btn)
        layout.add_widget(self.message_label)

        anchor.add_widget(layout)
        self.add_widget(anchor)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def go_to_login(self, button):
        self.manager.current = "login"

    def register(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        fullname = self.fullname_input.text
        config = get_config()
        asyncio.run_coroutine_threadsafe(self._register(email, password, fullname), config.global_event_loop)

    async def _register(self, email, password, full_name):
        success, result = await self.viewmodel.registration(email, password, full_name)

        if success:
            msg = f"Успешная регистрация"
        else:
            msg = f"Ошибка: {result}"

        Clock.schedule_once(lambda dt: setattr(self.message_label, "text", msg))

    def update_message(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.message_label, 'text', msg))

