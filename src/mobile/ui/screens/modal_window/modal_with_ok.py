from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock


def show_modal(text: str):
    modal = ModalView(
        size_hint=(0.8, 0.6),
        auto_dismiss=False
    )

    root = BoxLayout(
        orientation="vertical",
        padding=20,
        spacing=15
    )

    # ===== Scroll зона =====
    scroll = ScrollView(
        size_hint=(1, 1)
    )

    label = Label(
        text=text,
        size_hint_y=None,
        halign="left",
        valign="top"
    )

    # Автоматическая высота по тексту
    label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))

    # Пересчёт ширины текста при ресайзе
    scroll.bind(
        width=lambda inst, val: setattr(label, "text_size", (val - 20, None))
    )

    scroll.add_widget(label)

    # ===== Кнопка =====
    btn = Button(
        text="OK",
        size_hint_y=None,
        height=45
    )

    btn.bind(on_release=modal.dismiss)

    root.add_widget(scroll)
    root.add_widget(btn)

    modal.add_widget(root)

    # Чтобы текст корректно отрисовался сразу
    Clock.schedule_once(lambda dt: setattr(label, "text_size", (scroll.width - 20, None)))

    modal.open()
