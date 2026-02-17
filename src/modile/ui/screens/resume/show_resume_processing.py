import asyncio
from typing import Optional

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button

from src.api_client.models import ProcessingDetailOut
from src.modile.config import get_config
from src.modile.ui.screens.modal_window.modal_with_ok import show_modal
from src.modile.ui.screens.modal_window.modal_yes_or_no import show_confirm_modal
from src.modile.view_models.resume import ResumeModel
from src.modile.view_models.processing import ProcessingModel


class ResumeProcessingScreen(Screen):
    def __init__(
        self,
        resume_model: ResumeModel,
        processing_model: ProcessingModel,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.resume_model = resume_model
        self.processing_model = processing_model

        self.current_resume_id: Optional[int] = None
        self.current_requirement_id: Optional[int] = None
        self.current_processing_id: Optional[int] = None
        self.full_resume: Optional[str] = None

        # ===== Фон =====
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = FloatLayout()
        self.add_widget(root)

        # ===== Назад =====
        back_btn = Button(
            text="Назад",
            size_hint=(None, None),
            size=(80, 40),
            pos_hint={"x": 0.02, "top": 0.98},
            background_normal='',
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_release=lambda *_: self.manager.safe_switch("requirement_detail"))
        root.add_widget(back_btn)

        # ===== Основной контейнер =====
        self.vbox = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=[20, 70, 20, 20],
            size_hint=(1, 1)
        )
        root.add_widget(self.vbox)

        # ===== Блок РЕЗЮМЕ =====
        self.resume_scroll = ScrollView(
            size_hint=(1, 0.2),
        )
        self.resume_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=(0, 0, 0)
        )
        self.resume_label.bind(texture_size=self._update_resume_height)
        self.resume_scroll.add_widget(self.resume_label)

        self.vbox.add_widget(self.resume_scroll)

        # ===== Блок ОБРАБОТКИ =====
        self.processing_scroll = ScrollView(size_hint=(1, 0.4))
        self.processing_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=(0, 0, 0)
        )
        self.processing_label.bind(texture_size=self._update_processing_height)
        self.processing_scroll.add_widget(self.processing_label)

        self.vbox.add_widget(self.processing_scroll)

        # ===== Кнопки для обработки =====
        self.processing_actions = BoxLayout(size_hint=(1, None), height=45, spacing=10)
        self.show_resume_btn = Button(
            text="Просмотреть резюме",
            background_normal='',
            background_color=(0.3, 0.6, 0.95, 1)
        )
        self.show_resume_btn.bind(on_release=self.show_full_resume)

        self.create_processing_btn = Button(
            text="Создать обработку",
            background_normal='',
            background_color=(0.3, 0.6, 0.95, 1)
        )
        self.create_processing_btn.bind(on_release=self.create_processing)

        self.delete_processing_btn = Button(
            text="Удалить обработку",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1)
        )
        self.delete_processing_btn.bind(on_release=self.delete_processing)

        self.delete_resume_btn = Button(
            text="Удалить резюме",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1)
        )
        self.delete_resume_btn.bind(on_release=self.delete_resume)

        self.processing_actions.add_widget(self.show_resume_btn)
        self.processing_actions.add_widget(self.create_processing_btn)
        self.processing_actions.add_widget(self.delete_resume_btn)
        self.processing_actions.add_widget(self.delete_processing_btn)
        self.vbox.add_widget(self.processing_actions)

    # PUBLIC API

    def load(self, requirement_id: int, resume_id: int, full_resume: str):
        self.current_requirement_id = requirement_id
        self.current_resume_id = resume_id
        self.full_resume = full_resume
        self._load_resume()
        self._load_processing()

    # LOAD DATA

    def _load_resume(self):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.resume_model.get_resume(resume_id=self.current_resume_id),
            conf.global_event_loop
        )
        fut.add_done_callback(self._on_resume_loaded)

    def _on_resume_loaded(self, fut):
        try:
            resumes = fut.result()
            resume = resumes[0]
        except Exception as e:
            Clock.schedule_once(lambda dt, err=e: show_modal(f"Ошибка: {err}"))
            return

        Clock.schedule_once(lambda dt: self._set_resume(resume.resume))

    def _set_resume(self, text: str):
        self.resume_label.text = text
        self.resume_label.text_size = (self.width * 0.9, None)

    def _load_processing(self):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.processing_model.get_processing(self.current_resume_id),
            conf.global_event_loop
        )
        fut.add_done_callback(self._on_processing_loaded)

    def _on_processing_loaded(self, fut):
        try:
            processing = fut.result()
        except Exception:
            Clock.schedule_once(lambda dt: self._no_processing())
            return

        Clock.schedule_once(lambda dt: self._set_processing(processing))

    def _set_processing(self, processing: ProcessingDetailOut):
        self.current_processing_id = processing.processing_id

        if not processing.success:
            self.processing_label.text = (
                "Обработка завершилась с ошибкой.\n\n"
                f"Причина: {processing.message_error}\n"
                f"Попробуйте снова через {processing.wait_seconds} сек."
            )
        else:
            matches = "\n".join(f"• {item}" for item in processing.matches)
            self.processing_label.text = (
                "Результат обработки:\n\n"
                f"Оценка: {processing.score}\n"
                f"Вердикт: {processing.verdict}\n\n"
                f"Совпадения:\n{matches}\n\n"
                f"Рекомендация:\n{processing.recommendation}"
            )
        self.processing_label.text_size = (self.width * 0.9, None)

        self.create_processing_btn.disabled = True
        self.delete_processing_btn.disabled = False

    def _no_processing(self):
        self.processing_label.text = "Обработка отсутствует"
        self.create_processing_btn.disabled = False
        self.delete_processing_btn.disabled = True

    # ACTIONS

    def show_full_resume(self, *args):
        if self.full_resume:
            show_modal(self.full_resume)

    def delete_resume(self, *_):
        show_confirm_modal(
            "Удалить резюме?",
            on_yes=lambda: self._delete_resume_async()
        )

    def _delete_resume_async(self):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.resume_model.delete_resume([self.current_resume_id]),
            conf.global_event_loop
        )
        fut.add_done_callback(lambda f: Clock.schedule_once(
            lambda dt: self.manager.safe_switch("requirement_detail")
        ))

    def create_processing(self, *_):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.processing_model.create_new_processing(
                self.current_requirement_id,
                self.current_resume_id,
            ),
            conf.global_event_loop
        )
        fut.add_done_callback(lambda f: Clock.schedule_once(
            lambda dt: show_modal("Обработка запущена, в скором времени данные появятся на данной форме")
        ))

    def delete_processing(self, *_):
        if not self.current_processing_id:
            return

        show_confirm_modal(
            "Удалить обработку?",
            on_yes=lambda: self._delete_processing_async()
        )

    def _delete_processing_async(self):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.processing_model.delete_processing([self.current_processing_id]),
            conf.global_event_loop
        )
        fut.add_done_callback(lambda f: Clock.schedule_once(
            lambda dt: self._no_processing()
        ))

    # UI UTILS

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _update_resume_height(self, instance, size):
        self.resume_label.height = self.resume_label.texture_size[1]

    def _update_processing_height(self, instance, size):
        self.processing_label.height = self.processing_label.texture_size[1]
