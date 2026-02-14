import asyncio
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from src.modile.config import get_config
from src.modile.ui.screens.modal_window.modal_with_ok import show_modal
from src.modile.view_models.requirements import RequirementsModel


class CreateRequirementScreen(Screen):
    def __init__(self, viewmodel: RequirementsModel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = FloatLayout()
        self.add_widget(root)

        back_btn = Button(
            text="Назад",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={"x": 0.02, "top": 0.98},
            background_normal='',
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_release=self.go_back)
        root.add_widget(back_btn)

        container = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 80, 20, 20],  # отступы от краёв
            size_hint=(1, 1)
        )
        root.add_widget(container)

        self.input_field = TextInput(
            hint_text="Введите новое требование...",
            multiline=True,
            size_hint=(1, 1),
            background_normal='',
            background_color=(1, 1, 1, 1)
        )

        add_btn = Button(
            text="Добавить",
            size_hint=(1, None),
            height=50,
            background_normal='',
            background_color=(0.2, 0.6, 0.95, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.add_requirement)

        container.add_widget(self.input_field)
        container.add_widget(add_btn)


    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def go_back(self, *args):
        self.manager.safe_switch("all_requirements")

    def add_requirement(self, *args):
        text = self.input_field.text.strip()

        if not text:
            show_modal("Поле не может быть пустым")
            return

        conf = get_config()
        future = asyncio.run_coroutine_threadsafe(
            self._create_requirement(text),
            conf.global_event_loop
        )
        future.add_done_callback(self._on_create_done)

    async def _create_requirement(self, text: str):
        return await self.viewmodel.create_new_requirement(text)

    def _on_create_done(self, future):
        try:
            future.result()
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=e: show_modal(f"Ошибка: {err}")
            )
            return

        Clock.schedule_once(lambda dt: self._on_success())

    def _on_success(self):
        self.input_field.text = ""
        show_modal("Требование успешно добавлено")
        self.manager.current = "all_requirements"
