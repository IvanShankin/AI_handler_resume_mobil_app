import asyncio
import threading

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from src.api_client.base import BaseAPIClient, TokenManager
from src.api_client.services.auth import AuthClient
from src.api_client.services.processing import ProcessingClient
from src.api_client.services.requirements import RequirementClient
from src.api_client.services.resume import ResumeClient
from src.modile.config import get_config
from src.modile.ui.screens.auth.login import LoginScreen
from src.modile.ui.screens.auth.register import RegisterScreen
from src.modile.ui.screens.requirements.all_requirements import AllRequirementsScreen
from src.modile.ui.screens.requirements.new_requirement import CreateRequirementScreen
from src.modile.ui.screens.requirements.show_requirement import RequirementDetailScreen
from src.modile.ui.screens.resume.new_resume import CreateResumeScreen
from src.modile.ui.screens.resume.show_resume_processing import ResumeProcessingScreen
from src.modile.utils.event_loop import start_loop
from src.modile.view_models.auth_vm import AuthViewModel, RegViewModel
from src.modile.view_models.processing import ProcessingModel
from src.modile.view_models.requirements import RequirementsModel
from src.modile.view_models.resume import ResumeModel


class RootScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # белый фон
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def safe_switch(self, screen_name):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self, "current", screen_name))


class AuthApp(App):
    def build(self):
        conf = get_config()

        sm = RootScreenManager(transition=FadeTransition(duration=0.15))

        self.loop = asyncio.get_event_loop()
        self.base_client = BaseAPIClient(conf.base_url)
        self.auth_client = AuthClient(self.base_client)
        token_manager = TokenManager(self.auth_client)
        self.base_client.set_token_manager(token_manager)

        self.req_client = RequirementClient(self.base_client)
        self.resum_client = ResumeClient(self.base_client)
        self.processing_client = ProcessingClient(self.base_client)

        self.resume_proseccing_screen = ResumeProcessingScreen(
            name="show_resume_processing",
            resume_model=ResumeModel(resum_client=self.resum_client),
            processing_model=ProcessingModel(proc_client=self.processing_client)
        )
        self.requirements_detail = RequirementDetailScreen(
            name="requirement_detail",
            resume_screen=self.resume_proseccing_screen,
            viewmodel_req=RequirementsModel(req_client=self.req_client),
            viewmodel_resum=ResumeModel(self.resum_client)
        )

        sm.add_widget(LoginScreen(name="login", viewmodel=AuthViewModel(auth_client=self.auth_client)))
        sm.add_widget(RegisterScreen(name="register", viewmodel=RegViewModel(auth_client=self.auth_client)))
        sm.add_widget(
            AllRequirementsScreen(
                name="all_requirements",
                viewmodel=RequirementsModel(req_client=self.req_client),
                requirements_detail=self.requirements_detail
            )
        )
        sm.add_widget(CreateRequirementScreen(name="create_requirement", viewmodel=RequirementsModel(req_client=self.req_client)))
        sm.add_widget(CreateResumeScreen(name="create_resume", viewmodel=ResumeModel(resum_client=self.resum_client)))
        sm.add_widget(self.resume_proseccing_screen)
        sm.add_widget(self.requirements_detail)

        # Запускаем глобальный event loop в отдельном потоке
        t = threading.Thread(target=start_loop, args=(conf.global_event_loop,), daemon=True)
        t.start()

        return sm

    def on_stop(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.base_client.close())
