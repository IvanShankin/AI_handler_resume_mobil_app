import asyncio
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

from src.modile.config import get_config
from src.modile.ui.screens.modal_window.modal_with_ok import show_modal
from src.modile.view_models.requirements import RequirementsModel

BG_COLOR = (0.96, 0.96, 0.97, 1)
PANEL_COLOR = (0.985, 0.985, 0.99, 1)
TEXT_COLOR = (0.14, 0.14, 0.16, 1)
SUBTLE_COLOR = (0.35, 0.35, 0.38, 1)
BTN_NEUTRAL_BG = (0.22, 0.22, 0.24, 1)
BTN_PRIMARY_BG = (0.28, 0.28, 0.31, 1)


class CreateRequirementScreen(Screen):
    def __init__(self, viewmodel: RequirementsModel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = FloatLayout()
        self.add_widget(root)

        back_btn = Button(
            text="Назад",
            size_hint=(None, None),
            size=(92, 42),
            pos_hint={"x": 0.03, "top": 0.965},
            background_normal='',
            background_color=BTN_NEUTRAL_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        back_btn.bind(on_release=self.go_back)
        root.add_widget(back_btn)

        panel = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=[24, 88, 24, 24],
            size_hint=(0.95, 0.95),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        root.add_widget(panel)

        with panel.canvas.before:
            Color(*PANEL_COLOR)
            self.panel_bg = RoundedRectangle(pos=panel.pos, size=panel.size, radius=[18])
        panel.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

        title = Label(
            text="Новое требование",
            size_hint=(1, None),
            height=40,
            color=TEXT_COLOR,
            font_size=24,
            bold=True,
        )
        panel.add_widget(title)

        subtitle = Label(
            text="Опишите требование для обработки резюме",
            size_hint=(1, None),
            height=24,
            color=SUBTLE_COLOR,
            font_size=14,
        )
        panel.add_widget(subtitle)

        self.input_field = TextInput(
            hint_text="Введите новое требование...",
            multiline=True,
            size_hint=(1, 1),
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=TEXT_COLOR,
            cursor_color=TEXT_COLOR,
            padding=(14, 14),
        )

        add_btn = Button(
            text="Добавить",
            size_hint=(1, None),
            height=52,
            background_normal='',
            background_color=BTN_PRIMARY_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        add_btn.bind(on_release=self.add_requirement)

        panel.add_widget(self.input_field)
        panel.add_widget(add_btn)

    def _update_panel_bg(self, instance, *_):
        self.panel_bg.pos = instance.pos
        self.panel_bg.size = instance.size

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def go_back(self, *args):
        self.manager.safe_switch("all_requirements")

    def add_requirement(self, *args):
        text = self.input_field.text.strip()
        max_char = get_config().max_char_requirements

        if len(text) > max_char:
            show_modal(f"Слишком длинное требование. \n\nМаксимальная длинна символов у требования: {max_char}")
            return

        if not text:
            show_modal("Поле не может быть пустым")
            return

        conf = get_config()
        future = asyncio.run_coroutine_threadsafe(
            self._create_requirement(text),
            conf.global_event_loop
        )
        future.add_done_callback(self._on_create_done)

    async def _create_requirement(self, text: str) -> bool:
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
