from kivy.graphics import Color, RoundedRectangle
from kivy.uix.button import Button


class RoundButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(0.2, 0.6, 0.95, 1)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.width / 2])

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.bg.radius = [self.width / 2]
