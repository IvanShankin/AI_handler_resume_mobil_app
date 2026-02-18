import asyncio
from typing import Optional

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
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
from src.modile.utils.core_logger import get_logger
from src.modile.view_models.resume import ResumeModel
from src.modile.view_models.processing import ProcessingModel

BG_COLOR = (0.96, 0.96, 0.97, 1)
PANEL_COLOR = (0.985, 0.985, 0.99, 1)
TEXT_COLOR = (0.14, 0.14, 0.16, 1)
BTN_NEUTRAL_BG = (0.22, 0.22, 0.24, 1)
BTN_PRIMARY_BG = (0.28, 0.28, 0.31, 1)
BTN_DANGER_BG = (0.4, 0.4, 0.43, 1)


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

        self._processing_poll_event = None
        self._is_active = False
        self._is_processing_request_in_flight = False
        self._processing_poll_attempts = 0
        self._max_processing_poll_attempts = 20

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
        back_btn.bind(on_release=lambda *_: self.manager.safe_switch("requirement_detail"))
        root.add_widget(back_btn)

        self.vbox = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=[24, 78, 24, 24],
            size_hint=(0.96, 0.96),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        root.add_widget(self.vbox)

        with self.vbox.canvas.before:
            Color(*PANEL_COLOR)
            self.panel_bg = RoundedRectangle(pos=self.vbox.pos, size=self.vbox.size, radius=[18])
        self.vbox.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

        self.resume_title = Label(
            text="Резюме",
            size_hint=(1, None),
            height=28,
            color=TEXT_COLOR,
            font_size=18,
            bold=True,
        )
        self.vbox.add_widget(self.resume_title)

        self.resume_scroll = ScrollView(size_hint=(1, 0.24), bar_color=(0.5, 0.5, 0.55, 0.7), bar_inactive_color=(0.75, 0.75, 0.78, 0.3))
        self.resume_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=TEXT_COLOR,
            font_size=16,
        )
        self.resume_label.bind(texture_size=self._update_resume_height)
        self.resume_scroll.add_widget(self.resume_label)
        self.vbox.add_widget(self.resume_scroll)

        self.processing_title = Label(
            text="Обработка",
            size_hint=(1, None),
            height=28,
            color=TEXT_COLOR,
            font_size=18,
            bold=True,
        )
        self.vbox.add_widget(self.processing_title)

        self.processing_scroll = ScrollView(size_hint=(1, 0.42), bar_color=(0.5, 0.5, 0.55, 0.7), bar_inactive_color=(0.75, 0.75, 0.78, 0.3))
        self.processing_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=TEXT_COLOR,
            font_size=16,
        )
        self.processing_label.bind(texture_size=self._update_processing_height)
        self.processing_scroll.add_widget(self.processing_label)

        self.vbox.add_widget(self.processing_scroll)

        self.processing_actions = BoxLayout(size_hint=(1, None), height=48, spacing=10)
        self.show_resume_btn = Button(
            text="Просмотреть резюме",
            background_normal='',
            background_color=BTN_PRIMARY_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.show_resume_btn.bind(on_release=self.show_full_resume)

        self.create_processing_btn = Button(
            text="Создать обработку",
            background_normal='',
            background_color=BTN_PRIMARY_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.create_processing_btn.bind(on_release=self.create_processing)

        self.delete_processing_btn = Button(
            text="Удалить обработку",
            background_normal='',
            background_color=BTN_DANGER_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.delete_processing_btn.bind(on_release=self.delete_processing)

        self.delete_resume_btn = Button(
            text="Удалить резюме",
            background_normal='',
            background_color=BTN_DANGER_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.delete_resume_btn.bind(on_release=self.delete_resume)

        self.processing_actions.add_widget(self.show_resume_btn)
        self.processing_actions.add_widget(self.create_processing_btn)
        self.processing_actions.add_widget(self.delete_resume_btn)
        self.processing_actions.add_widget(self.delete_processing_btn)
        self.vbox.add_widget(self.processing_actions)

    def _update_panel_bg(self, instance, *_):
        self.panel_bg.pos = instance.pos
        self.panel_bg.size = instance.size

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _update_resume_height(self, instance, value):
        instance.height = value[1]

    def _update_processing_height(self, instance, value):
        instance.height = value[1]

    def load(self, requirement_id: int, resume_id: int, full_resume: str):
        self._is_active = True
        self.current_requirement_id = requirement_id
        self.current_resume_id = resume_id
        self.full_resume = full_resume
        self._load_resume()
        self._load_processing()

    def on_enter(self, *args):
        self._is_active = True
        return super().on_enter(*args)

    def on_leave(self, *args):
        self._is_active = False
        self._stop_processing_polling()
        return super().on_leave(*args)

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
        self._is_processing_request_in_flight = False

        if not self._is_active:
            return

        try:
            processing = fut.result()
        except Exception:
            get_logger(__name__).exception("Ошибка при загрузке processing")
            Clock.schedule_once(lambda dt: self._no_processing(during_poll=self._is_polling_active()))
            return

        Clock.schedule_once(lambda dt: self._set_processing(processing))

    def _set_processing(self, processing: ProcessingDetailOut):
        self.current_processing_id = processing.processing_id
        self._stop_processing_polling()

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

    def _no_processing(self, during_poll: bool = False):
        self.processing_label.text = "Обработка отсутствует"
        self.create_processing_btn.disabled = during_poll
        self.delete_processing_btn.disabled = True

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
        fut.add_done_callback(self._on_processing_created)

    def _on_processing_created(self, fut):
        try:
            created = fut.result()
        except Exception as e:
            Clock.schedule_once(lambda dt, err=e: show_modal(f"Ошибка запуска обработки: {err}"))
            return

        if not created:
            Clock.schedule_once(lambda dt: show_modal("Не удалось запустить обработку"))
            return

        def _show_and_start(_):
            if not self._is_active:
                return
            self.create_processing_btn.disabled = True
            show_modal("Обработка запущена, в скором времени данные появятся на данной форме")
            self._start_processing_polling()

        Clock.schedule_once(_show_and_start)

    def _start_processing_polling(self):
        self._stop_processing_polling()
        self._processing_poll_attempts = 0
        self._processing_poll_event = Clock.schedule_interval(self._poll_processing_status, 3)

    def _stop_processing_polling(self):
        if self._processing_poll_event is not None:
            self._processing_poll_event.cancel()
            self._processing_poll_event = None
        self._processing_poll_attempts = 0
        self._is_processing_request_in_flight = False

    def _is_polling_active(self) -> bool:
        return self._processing_poll_event is not None

    def _poll_processing_status(self, _dt):
        if not self._is_active or not self.current_resume_id:
            self._stop_processing_polling()
            return

        if self._is_processing_request_in_flight:
            return

        if self._processing_poll_attempts >= self._max_processing_poll_attempts:
            self._stop_processing_polling()
            self.create_processing_btn.disabled = False
            show_modal("Достигнут лимит запросов статуса обработки. Попробуйте обновить позже.")
            return

        self._processing_poll_attempts += 1
        self._is_processing_request_in_flight = True
        self._load_processing()

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
