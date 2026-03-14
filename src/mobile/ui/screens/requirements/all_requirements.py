import asyncio
from typing import Optional, List

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

from src.api_client.schemas import RequirementsOut
from src.mobile.config import get_config
from src.mobile.ui.elements.buttons import RoundButton
from src.mobile.ui.screens.modal_window.modal_with_ok import show_modal
from src.mobile.ui.screens.requirements.show_requirement import RequirementDetailScreen
from src.mobile.view_models.requirements import RequirementsModel

MIN_CELL_WIDTH = dp(260)
CARD_HEIGHT = dp(120)

BG_COLOR = (0.92, 0.92, 0.92, 1)
PANEL_COLOR = (0.92, 0.92, 0.92, 1)
CARD_COLOR = (1, 1, 1, 1)
TEXT_COLOR = (0.14, 0.14, 0.16, 1)
SUBTLE_TEXT_COLOR = (0.35, 0.35, 0.38, 1)
BTN_NEUTRAL_BG = (2.2, 2.2, 2.2, 1)
FAB_BG = (0.2, 0.2, 0.22, 1)


class AllRequirementsScreen(Screen):
    def __init__(self, viewmodel: RequirementsModel, requirements_detail: RequirementDetailScreen, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel
        self.requirements_detail = requirements_detail

        with self.canvas.before:
            Color(*BG_COLOR)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = FloatLayout()
        self.add_widget(root)

        container = AnchorLayout(anchor_x="center", anchor_y="top", size_hint=(1, 1), padding=(dp(16), dp(22), dp(16), dp(16)))
        root.add_widget(container)

        with container.canvas.before:
            Color(*PANEL_COLOR)
            self.panel = RoundedRectangle(pos=container.pos, size=container.size, radius=[dp(18)])
        container.bind(pos=self._update_panel, size=self._update_panel)

        vbox = BoxLayout(orientation="vertical", spacing=dp(14), padding=(dp(18), dp(52), dp(18), dp(18)), size_hint=(0.99, 0.99))
        container.add_widget(vbox)

        back_btn = Button(
            text="Выйти",
            size_hint=(None, None),
            size=(dp(92), dp(42)),
            pos_hint={"x": 0.03, "top": 0.965},
            background_color=BTN_NEUTRAL_BG,
            color=(1, 1, 1, 1),
            bold=True,
        )
        back_btn.bind(on_release=self.go_exit)
        root.add_widget(back_btn)

        title = Label(
            text="Список всех требований",
            color=TEXT_COLOR,
            size_hint=(1, None),
            height=dp(40),
            font_size=sp(24),
            bold=True,
        )
        vbox.add_widget(title)

        subtitle = Label(
            text="Выберите требование для просмотра деталей",
            color=SUBTLE_TEXT_COLOR,
            size_hint=(1, None),
            height=dp(26),
            font_size=sp(14),
        )
        vbox.add_widget(subtitle)

        self.scroll = ScrollView(size_hint=(1, 1), bar_color=(0.5, 0.5, 0.55, 0.7), bar_inactive_color=(0.75, 0.75, 0.78, 0.3))
        vbox.add_widget(self.scroll)

        self.grid = GridLayout(cols=1, spacing=dp(12), padding=dp(6), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)

        fab = RoundButton(
            text="+",
            font_size=sp(36),
            size_hint=(None, None),
            size=(dp(62), dp(62)),
            pos_hint={'center_x': 0.5, 'y': 0.022},
            background_color=FAB_BG,
            color=(1, 1, 1, 1),
        )
        fab.bind(on_release=self.on_add_requirement)
        root.add_widget(fab)

        self.bind(size=self._update_cols)
        self.grid.bind(width=lambda *_: self._update_cols())

    def _update_panel(self, instance, *_):
        self.panel.pos = instance.pos
        self.panel.size = instance.size

    def go_exit(self, *args):
        get_config().token_storage.clear_tokens()
        self.manager.safe_switch("login")

    def on_pre_enter(self, *args):
        if not get_config().token_storage.get_access_token():
            self.manager.safe_switch("login")
            return
        self.load_requirements()

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _update_cols(self, *args):
        width = self.width * 0.96
        cols = max(1, int(width // MIN_CELL_WIDTH))
        self.grid.cols = cols

        for child in list(self.grid.children):
            child.size_hint_x = 1.0 / cols

    def load_requirements(self, requirement_id: Optional[int] = None):
        conf = get_config()
        fut = asyncio.run_coroutine_threadsafe(
            self.viewmodel.get_requirements(requirement_id),
            conf.global_event_loop
        )
        fut.add_done_callback(self._on_requirements_future)

    def _on_requirements_future(self, fut):
        try:
            requirements: List[RequirementsOut] = fut.result()
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=e: show_modal(f"Ошибка при загрузке: {err}")
            )
            return
        Clock.schedule_once(lambda dt: self.populate_requirements(requirements))

    def populate_requirements(self, requirements: List[RequirementsOut]):
        self.grid.clear_widgets()
        for req in requirements:
            text = (req.requirements[:120] + "…") if len(req.requirements) > 120 else req.requirements
            btn = Button(
                color=TEXT_COLOR,
                text=text,
                size_hint_y=None,
                height=CARD_HEIGHT,
                halign="left",
                valign="middle",
                text_size=(None, None),
                background_normal='',
                background_color=CARD_COLOR,
                padding=(dp(16), dp(10)),
            )
            btn.text_size = (self._calc_cell_inner_width(), CARD_HEIGHT - dp(22))
            btn.halign = "left"
            btn.valign = "middle"

            btn.bind(on_release=lambda inst, r=req: self.open_requirement(r))
            self.grid.add_widget(btn)

        self._update_cols()

    def _calc_cell_inner_width(self):
        cols = max(1, self.grid.cols)
        return max(dp(100), (self.width * 0.96) / cols - dp(30))

    def open_requirement(self, requirement: RequirementsOut):
        self.requirements_detail.set_requirement(requirement=requirement)
        self.manager.safe_switch("requirement_detail")

    def on_add_requirement(self, instance):
        self.manager.safe_switch("create_requirement")
