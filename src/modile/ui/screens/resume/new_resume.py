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
from src.modile.view_models.resume import ResumeModel


class CreateResumeScreen(Screen):
    def __init__(self, viewmodel: ResumeModel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.requirement_id: int | None = None

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        root = FloatLayout()
        self.add_widget(root)

        back_btn = Button(
            text="Назад",
            size_hint=(None, None),
            size=(80, 40),
            pos_hint={"x": 0.02, "top": 0.98},
            background_normal='',
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_release=self.go_back)
        root.add_widget(back_btn)

        container = BoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 80, 20, 20],
            size_hint=(1, 1)
        )
        root.add_widget(container)

        self.input_field = TextInput(
            hint_text="Введите текст резюме...",
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
        add_btn.bind(on_release=self.add_resume)

        container.add_widget(self.input_field)
        container.add_widget(add_btn)


    def set_requirement_id(self, requirement_id: int):
        """
        Вызывается перед переходом на экран,
        чтобы указать к какому требованию создаётся резюме
        """
        self.requirement_id = requirement_id

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def go_back(self, *args):
        self.manager.safe_switch("requirement_detail")


    def add_resume(self, *args):
        text = self.input_field.text.strip()

        if not text:
            show_modal("Поле не может быть пустым")
            return

        if not self.requirement_id:
            show_modal("Не указан requirement_id")
            return

        conf = get_config()

        future = asyncio.run_coroutine_threadsafe(
            self._create_resume(self.requirement_id, text),
            conf.global_event_loop
        )

        future.add_done_callback(self._on_create_done)

    async def _create_resume(self, requirement_id: int, text: str) -> bool:
        return await self.viewmodel.create_resume(requirement_id, text)

    def _on_create_done(self, future):
        try:
            result = future.result()
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=e: show_modal(f"Ошибка: {err}")
            )
            return

        if not result:
            Clock.schedule_once(
                lambda dt: show_modal("Не удалось создать резюме")
            )
            return

        Clock.schedule_once(lambda dt: self._on_success())

    def _on_success(self):
        self.input_field.text = ""
        show_modal("Резюме успешно добавлено")

        # возвращаемся обратно к деталям требования
        self.manager.safe_switch("requirement_detail")
