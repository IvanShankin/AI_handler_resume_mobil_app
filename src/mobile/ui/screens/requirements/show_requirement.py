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
from kivy.metrics import dp, sp

from src.api_client.schemas import RequirementsOut, ResumeOut
from src.mobile.config import get_config
from src.mobile.ui.elements.buttons import RoundButton
from src.mobile.ui.screens.modal_window.modal_with_ok import show_modal
from src.mobile.ui.screens.modal_window.modal_yes_or_no import show_confirm_modal
from src.mobile.ui.screens.resume.show_resume_processing import ResumeProcessingScreen
from src.mobile.view_models.requirements import RequirementsModel
from src.mobile.view_models.resume import ResumeModel

MIN_CELL_WIDTH = dp(260)
CARD_HEIGHT = dp(120)


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
        self._conf = get_config()

        self.requirement_id: Optional[int] = None
        self.requirement: Optional[RequirementsOut] = None
        self._resumes_cache: List[ResumeOut] = []
        self._resumes_loaded = False

        with self.canvas.before:
            Color(*self._conf.bg_color)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = FloatLayout()
        self.add_widget(root)

        container = AnchorLayout(anchor_x="center", anchor_y="top", padding=(dp(16), dp(22), dp(16), dp(16)))
        root.add_widget(container)

        with container.canvas.before:
            Color(*self._conf.panel_color)
            self.panel_bg = RoundedRectangle(pos=container.pos, size=container.size, radius=[dp(18)])
        container.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

        back_btn = Button(
            text="Назад",
            size_hint=(None, None),
            size=(dp(92), dp(42)),
            pos_hint={"x": 0.03, "top": 0.965},
            background_normal='',
            background_color=self._conf.btn_neutral_bg_soft,
            color=(1, 1, 1, 1),
            bold=True,
        )
        back_btn.bind(on_release=self.go_back)
        root.add_widget(back_btn)

        self.vbox = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=(dp(18), dp(52), dp(18), dp(18)),
            size_hint=(0.99, 0.99)
        )
        container.add_widget(self.vbox)

        self.title = Label(
            text="Требование",
            size_hint=(1, None),
            height=dp(42),
            color=self._conf.text_color,
            font_size=sp(24),
            bold=True,
        )
        self.vbox.add_widget(self.title)

        self.req_scroll = ScrollView(size_hint=(1, None), height=dp(130))

        self.req_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=self._conf.text_color,
            font_size=sp(16),
        )

        self.req_label.bind(texture_size=self._update_req_height)
        self.req_scroll.bind(width=self._update_text_width)
        self.req_scroll.add_widget(self.req_label)
        self.vbox.add_widget(self.req_scroll)

        resume_title = Label(
            text="Резюме",
            size_hint=(1, None),
            height=dp(34),
            color=self._conf.subtle_text_color,
            font_size=sp(18),
            bold=True,
        )
        self.vbox.add_widget(resume_title)

        self.resume_scroll = ScrollView(size_hint=(1, 1), bar_color=(0.5, 0.5, 0.55, 0.7), bar_inactive_color=(0.75, 0.75, 0.78, 0.3))

        self.resume_grid = GridLayout(cols=1, spacing=dp(12), padding=dp(6), size_hint_y=None)
        self.resume_grid.bind(minimum_height=self.resume_grid.setter("height"))

        self.resume_scroll.add_widget(self.resume_grid)
        self.vbox.add_widget(self.resume_scroll)

        self.bind(size=self._update_resume_cols)
        self.resume_grid.bind(width=lambda *_: self._update_resume_cols())

        action_box = BoxLayout(size_hint=(1, None), height=dp(52), spacing=dp(10))

        self.show_full_btn = Button(
            text="Показать полностью",
            background_normal='',
            background_color=self._conf.btn_primary_bg,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.show_full_btn.bind(on_release=self.show_full_requirement)

        self.delete_btn = Button(
            text="Удалить",
            background_normal='',
            background_color=self._conf.btn_danger_bg,
            color=(1, 1, 1, 1),
            bold=True,
        )
        self.delete_btn.bind(on_release=self.delete_requirement)

        action_box.add_widget(self.show_full_btn)
        action_box.add_widget(self.delete_btn)

        self.vbox.add_widget(action_box)

        fab = RoundButton(
            text="+",
            font_size=sp(36),
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            pos_hint={'center_x': 0.5, 'y': 0.15},
            background_color=self._conf.fab_bg,
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
        return max(dp(100), (self.width * 0.96) / cols - dp(30))

    def _update_text_width(self, instance, value):
        self.req_label.text_size = (instance.width - dp(20), None)

    def set_requirement(self, requirement: RequirementsOut):
        self.requirement = requirement
        self.requirement_id = requirement.requirement_id
        self._resumes_cache = []
        self._resumes_loaded = False

    def on_pre_enter(self, *args):
        if not get_config().token_storage.get_access_token():
            self.manager.safe_switch("login")
            return

        if self.requirement:
            self.populate_requirement(self.requirement)
            if self._resumes_loaded:
                self.populate_resumes(self._resumes_cache)
            else:
                self.load_resumes()
        elif self.requirement_id:
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
            for req in data:
                if req.requirement_id == self.requirement_id:
                    requirement = req

        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=e: show_modal(f"Ошибка: {str(err)}")
            )
            return

        self.requirement = requirement
        self.requirement_id = requirement.requirement_id
        Clock.schedule_once(lambda dt: self.populate_requirement(requirement))
        if self._resumes_loaded:
            Clock.schedule_once(lambda dt: self.populate_resumes(self._resumes_cache))
        else:
            self.load_resumes()

    def populate_requirement(self, requirement: RequirementsOut):
        self.requirement = requirement
        short_text = (
            requirement.requirement[:300] + "..."
            if len(requirement.requirement) > 300
            else requirement.requirement
        )
        self.req_label.text = short_text

    def load_resumes(self):
        if not self.requirement_id:
            return
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

        self._resumes_cache = resumes
        self._resumes_loaded = True
        Clock.schedule_once(lambda dt: self.populate_resumes(self._resumes_cache))

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
                background_color=self._conf.card_color,
                color=self._conf.text_color,
                padding=(dp(16), dp(10)),
            )

            btn.text_size = (self._calc_resume_cell_width(), CARD_HEIGHT - dp(22))
            btn.bind(on_release=lambda inst, r=resume: self.open_resume(r))

            self.resume_grid.add_widget(btn)

        self._update_resume_cols()

    def add_resume_local(self, resume: ResumeOut):
        if not resume:
            return
        self._resumes_cache = [resume] + [
            item for item in self._resumes_cache
            if item.resume_id != resume.resume_id
        ]
        self._resumes_loaded = True
        if self.manager and self.manager.current == "requirement_detail":
            self.populate_resumes(self._resumes_cache)

    def remove_resume_local(self, resume_id: int):
        if resume_id is None:
            return
        self._resumes_cache = [
            item for item in self._resumes_cache
            if item.resume_id != resume_id
        ]
        self._resumes_loaded = True
        if self.manager and self.manager.current == "requirement_detail":
            self.populate_resumes(self._resumes_cache)

    def show_full_requirement(self, *args):
        if self.requirement:
            show_modal(self.requirement.requirement)

    def delete_requirement(self, *args):
        conf = get_config()

        def delete():
            fut = asyncio.run_coroutine_threadsafe(
                self.viewmodel_req.delete_requirements([self.requirement_id]),
                conf.global_event_loop
            )
            if fut.result():
                try:
                    all_screen = self.manager.get_screen("all_requirements")
                    all_screen.remove_requirement_local(self.requirement_id)
                except Exception:
                    pass
                self.requirement = None
                self.requirement_id = None
                self._resumes_cache = []
                self._resumes_loaded = False
                show_modal("Требование успешно удалено!")
                Clock.schedule_once(lambda dt: self.manager.safe_switch("all_requirements"))
            else:
                show_modal("Требование не найдено!")


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

