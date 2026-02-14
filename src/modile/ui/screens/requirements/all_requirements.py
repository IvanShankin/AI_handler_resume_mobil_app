import asyncio
from typing import Optional, List

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from src.api_client.models import RequirementsOut
from src.modile.config import get_config
from src.modile.ui.elements.buttons import RoundButton
from src.modile.ui.screens.modal_window.modal_with_ok import show_modal
from src.modile.view_models.requirements import RequirementsModel

MIN_CELL_WIDTH = 260  # минимальная ширина карточки (подбирай)
CARD_HEIGHT = 120     # высота карточки


class AllRequirementsScreen(Screen):
    def __init__(self, viewmodel: RequirementsModel, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = viewmodel

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Root float для абсолютного позиционирования FAB
        root = FloatLayout()
        self.add_widget(root)

        # Центральная вертикальная колонка (заголовок + scroll)
        container = AnchorLayout(anchor_x="center", anchor_y="top", size_hint=(1, 1))
        root.add_widget(container)

        vbox = BoxLayout(orientation="vertical", spacing=10, padding=16, size_hint=(0.98, 0.98))
        container.add_widget(vbox)

        title = Label(text="Список всех требований", color=(0,0,0), size_hint=(1, None), height=40)
        vbox.add_widget(title)

        # Scroll + grid (GridLayout внутри ScrollView)
        self.scroll = ScrollView(size_hint=(1, 1))
        vbox.add_widget(self.scroll)

        self.grid = GridLayout(cols=1, spacing=12, padding=6, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        # ширина grid управляется автоматически (size_hint_x=1 у ScrollView содержимого)
        self.scroll.add_widget(self.grid)

        # Кнопка добавления (FAB-подобная) — по центру снизу
        fab = RoundButton(
            text="+",
            font_size=40,
            size_hint=(None, None),
            size=(64, 64),
            pos_hint={'center_x': 0.5, 'y': 0.02},
        )
        fab.bind(on_release=self.on_add_requirement)
        root.add_widget(fab)

        # Пересчитываем количество колонок при изменении ширины экрана / контейнера
        self.bind(size=self._update_cols)
        self.grid.bind(width=lambda *_: self._update_cols())

    def on_pre_enter(self, *args):
        if not self.viewmodel.is_authenticated():
            self.manager.safe_switch("login")
            return
        self.load_requirements()

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _update_cols(self, *args):
        # вычисляем доступную ширину для контента (используем ширину Screen)
        width = self.width * 0.96  # немного отступа
        cols = max(1, int(width // MIN_CELL_WIDTH))
        # если ширина меньше MIN_CELL_WIDTH, cols==1
        self.grid.cols = cols

        # если cols > 1, задаём минимальную ширину для детей через size_hint_x
        # используем равномерное распределение: size_hint_x = 1/cols
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
        # очистка и заполнение grid
        self.grid.clear_widgets()
        for req in requirements:
            text = (req.requirements[:120] + "…") if len(req.requirements) > 120 else req.requirements
            btn = Button(
                text=text,
                size_hint_y=None,
                height=CARD_HEIGHT,
                halign="left",
                valign="middle",
                text_size=(None, None),
                background_normal='',
                background_color=(1, 1, 1, 1),
            )
            # корректное перенос и выравнивание текста
            btn.text_size = (self._calc_cell_inner_width(), CARD_HEIGHT - 20)
            btn.halign = "left"
            btn.valign = "middle"

            # сохранение замыкания: привязываем сам объект req
            btn.bind(on_release=lambda inst, r=req: self.open_requirement(r))

            # чтобы кнопка растягивалась в колонках, пусть size_hint_x будет установлено в _update_cols
            self.grid.add_widget(btn)

        # обновить кол-во колонок/children size_hint_x
        self._update_cols()

    def _calc_cell_inner_width(self):
        # приблизительная ширина текста внутри одной ячейки
        cols = max(1, self.grid.cols)
        return max(100, (self.width * 0.96) / cols - 24)

    def open_requirement(self, requirement: RequirementsOut):
        show_modal(f"Требование #{requirement.requirements_id}\n\n{requirement.requirements}")
        self.manager.safe_switch("pass")

    def on_add_requirement(self, instance):
        self.manager.safe_switch("create_requirement")
