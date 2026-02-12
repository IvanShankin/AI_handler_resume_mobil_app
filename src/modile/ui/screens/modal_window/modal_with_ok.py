from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

def show_modal(text: str):
    modal = ModalView(size_hint=(0.7, 0.4), auto_dismiss=False)

    layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

    label = Label(text=text)
    btn = Button(text="OK", size_hint_y=None, height=40)

    btn.bind(on_release=modal.dismiss)

    layout.add_widget(label)
    layout.add_widget(btn)

    modal.add_widget(layout)
    modal.open()