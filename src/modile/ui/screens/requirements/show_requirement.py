import asyncio
from typing import List, Optional

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from src.api_client.models import RequirementsOut, ResumeOut
from src.modile.config import get_config
from src.modile.ui.elements.buttons import RoundButton
from src.modile.ui.screens.modal_window.modal_with_ok import show_modal
from src.modile.ui.screens.modal_window.modal_yes_or_no import show_confirm_modal
from src.modile.ui.screens.resume.show_resume_processing import ResumeProcessingScreen
from src.modile.view_models.requirements import RequirementsModel
from src.modile.view_models.resume import ResumeModel

MIN_CELL_WIDTH = 260
CARD_HEIGHT = 120

BG_COLOR = (0.96, 0.96, 0.97, 1)
PANEL_COLOR = (0.985, 0.985, 0.99, 1)
CARD_COLOR = (1, 1, 1, 1)
TEXT_COLOR = (0.14, 0.14, 0.16, 1)
SUBTLE_TEXT = (0.35, 0.35, 0.38, 1)
BTN_NEUTRAL_BG = (0.22, 0.22, 0.24, 1)
BTN_PRIMARY_BG = (0.28, 0.28, 0.31, 1)
BTN_DANGER_BG = (0.4, 0.4, 0.43, 1)
FAB_BG = (0.2, 0.2, 0.22, 1)


class RequirementDetailScreen(Screen):

    def __init__(
        self,
        resume_screen: ResumeProcessingScreen,
        viewmodel_req: RequirementsModel,
        viewmodel_resum: ResumeModel,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.resume_screen = resume_screen

        self.viewmodel_req = viewmodel_req
        self.viewmodel_resum = viewmodel_resum

        self.requirement_id: Optional[int] = None
        self.requirement: Optional[RequirementsOut] = None

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

        container = AnchorLayout(anchor_x="center", anchor_y="top", padding=(16, 22, 16, 16))
        root.add_widget(container)

        with container.canvas.before:
            Color(*PANEL_COLOR)
            self.panel_bg = RoundedRectangle(pos=container.pos, size=container.size, radius=[18])
        container.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

        self.vbox = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=(18, 52, 18, 18),
            size_hint=(0.99, 0.99)
        )
        container.add_widget(self.vbox)

        self.title = Label(
            text="Требование",
            size_hint=(1, None),
            height=42,
            color=TEXT_COLOR,
            font_size=24,
            bold=True,
        )
        self.vbox.add_widget(self.title)

        self.req_scroll = ScrollView(size_hint=(1, None), height=130)

        self.req_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=TEXT_COLOR,
            font_size=16,
        )

        self.req_label.bind(texture_size=self._update_req_height)
        self.req_scroll.bind(width=self._update_text_width)
        self.req_scroll.add_widget(self.req_label)
        self.vbox.add_widget(self.req_scroll)

        resume_title = Label(
            text="Резюме",
            size_hint=(1, None),
            height=34,
            color=SUBTLE_TEXT,
            font_size=18,
            bold=True,
        )
        self.vbox.add_widget(resume_title)

        self.resume_scroll = ScrollView(size_hint=(1, 1), bar_color=(0.5, 0.5, 0.55, 0.7), bar_inactive_color=(0.75, 0.75, 0.78, 0.3))

        self.resume_grid = GridLayout(cols=1, spacing=12, padding=6, size_hint_y=None)
        self.resume_grid.bind(minimum_height=self.resume_grid.setter("height"))

        self.resume_scroll.add_widget(self.resume_grid)
        self.vbox.add_widget(self.resume_scroll)

        self.bind(size=self._update_resume_cols)
        self.resume_grid.bind(width=lambda *_: self._update_resume_cols())

        action_box = BoxLayout(size_hint=(1, None), height=52, spacing=10)

        self.show_full_btn = Button(
            text="Показать полностью",
            background_normal='',
            background_color=BTN_PRIMARY_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.show_full_btn.bind(on_release=self.show_full_requirement)

        self.delete_btn = Button(
            text="Удалить",
            background_normal='',
            background_color=BTN_DANGER_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.delete_btn.bind(on_release=self.delete_requirement)

        action_box.add_widget(self.show_full_btn)
        action_box.add_widget(self.delete_btn)

        self.vbox.add_widget(action_box)

        fab = RoundButton(
            text="+",
            font_size=36,
            size_hint=(None, None),
            size=(56, 56),
            pos_hint={'center_x': 0.5, 'y': 0.15},
            background_color=FAB_BG,
            color=(1, 1, 1, 1),
        )
        fab.bind(on_release=self.add_resume)
        root.add_widget(fab)

    def _update_panel_bg(self, instance, *_):
        self.panel_bg.pos = instance.pos
        self.panel_bg.size = instance.size

    def _update_resume_cols(self, *args):
        width = self.width * 0.96
        cols = max(1, int(width // MIN_CELL_WIDTH))
        self.resume_grid.cols = cols

        for child in list(self.resume_grid.children):
            child.size_hint_x = 1.0 / cols

    def _update_req_height(self, instance, value):
        instance.height = value[1]

    def _calc_resume_cell_width(self):
        cols = max(1, self.resume_grid.cols)
        return max(100, (self.width * 0.96) / cols - 30)

    def _update_text_width(self, instance, value):
        self.req_label.text_size = (instance.width - 20, None)

    def set_requirement(self, requirement: RequirementsOut):
        self.requirement = requirement
        self.requirement_id = requirement.requirements_id

    def on_pre_enter(self, *args):
        if not get_config().token_storage.get_access_token():
            self.manager.safe_switch("login")
            return

        if self.requirement_id:
            self.load_requirement()

    def load_requirement(self):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.viewmodel_req.get_requirements(self.requirement_id),
            conf.global_event_loop
        )
        fut.add_done_callback(self._on_loaded)

    def _on_loaded(self, fut):
        try:
            data: List[RequirementsOut] = fut.result()
            if not data:
                raise ValueError("Требование не найдено")
            requirement = data[0]
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=e: show_modal(f"Ошибка: {str(err)}")
            )
            return

        Clock.schedule_once(lambda dt: self.populate_requirement(requirement))

    def populate_requirement(self, requirement: RequirementsOut):
        self.requirement = requirement
        short_text = (
            requirement.requirements[:300] + "..."
            if len(requirement.requirements) > 300
            else requirement.requirements
        )
        self.req_label.text = short_text
        self.load_resumes()

    def load_resumes(self):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.viewmodel_resum.get_resume(requirement_id=self.requirement_id),
            conf.global_event_loop
        )
        fut.add_done_callback(self._on_resumes_loaded)

    def _on_resumes_loaded(self, fut):
        try:
            resumes: List[ResumeOut] = fut.result()
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=e: show_modal(f"Ошибка при загрузке резюме: {err}")
            )
            return

        Clock.schedule_once(lambda dt: self.populate_resumes(resumes))

    def populate_resumes(self, resumes: List[ResumeOut]):
        self.resume_grid.clear_widgets()

        for resume in resumes:
            text = (
                resume.resume[:120] + "..."
                if len(resume.resume) > 120
                else resume.resume
            )

            btn = Button(
                text=text,
                size_hint_y=None,
                height=CARD_HEIGHT,
                halign="left",
                valign="middle",
                background_normal='',
                background_color=CARD_COLOR,
                color=TEXT_COLOR,
                padding=(16, 10),
            )

            btn.text_size = (self._calc_resume_cell_width(), CARD_HEIGHT - 22)
            btn.bind(on_release=lambda inst, r=resume: self.open_resume(r))

            self.resume_grid.add_widget(btn)

        self._update_resume_cols()

    def show_full_requirement(self, *args):
        if self.requirement:
            show_modal(self.requirement.requirements)

    def delete_requirement(self, *args):
        conf = get_config()

        def delete():
            fut = asyncio.run_coroutine_threadsafe(
                self.viewmodel_req.delete_requirements([self.requirement_id]),
                conf.global_event_loop
            )
            if fut.result():
                show_modal("Требование успешно удалено!")
            else:
                show_modal("Требование не найдено!")

            fut.add_done_callback(lambda f: Clock.schedule_once(
                lambda dt: self.manager.safe_switch("all_requirements")
            ))

        show_confirm_modal(
            "Вы действительно хотите удалить требование?",
            on_yes=lambda: delete(),
            on_no=lambda: print("Отмена")
        )

    def add_resume(self, *args):
        screen = self.manager.get_screen("create_resume")
        screen.set_requirement_id(self.requirement_id)
        self.manager.safe_switch("create_resume")

    def open_resume(self, resume: ResumeOut):
        self.manager.safe_switch("show_resume_processing")
        self.resume_screen.load(
            requirement_id=self.requirement_id,
            resume_id=resume.resume_id,
            full_resume=resume.resume
        )

    def go_back(self, *args):
        self.manager.safe_switch("all_requirements")

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
