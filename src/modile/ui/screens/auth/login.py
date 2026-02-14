import asyncio

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from src.modile.config import get_config
from src.modile.ui.elements.creating_elements import create_textinput, create_button
from src.modile.ui.screens.modal_window.modal_with_ok import show_modal
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

        conf = get_config()
        future = asyncio.run_coroutine_threadsafe(
            self.viewmodel.check_refresh_token(),
            conf.global_event_loop
        )

        future.add_done_callback(self._on_refresh_done)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _on_refresh_done(self, future):
        try:
            success = future.result()
        except Exception:
            return

        if success:
            self.go_to_all_requirements()

    def go_to_register(self, *args):
        self.manager.safe_switch("register")

    def go_to_all_requirements(self, *args):
        self.manager.safe_switch("all_requirements")

    def login_clicked(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        conf = get_config()
        asyncio.run_coroutine_threadsafe(
            self._handle_login(username, password),
            conf.global_event_loop
        )

    def _show_error(self, message: str):
        show_modal(message)

    async def _handle_login(self, username, password):
        success, result = await self.viewmodel.login(username, password)

        if success:
            self.go_to_all_requirements()
        else:
            Clock.schedule_once(lambda dt: self._show_error(f"Ошибка: {result}"))
