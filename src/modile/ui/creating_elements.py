# --- Функция для создания "красивого" ввода ---
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


def create_textinput(hint, password=False):
    return TextInput(
        hint_text=hint,
        multiline=False,
        password=password,
        size_hint=(0.9, None),
        height=40,
        padding_y=(5,5)
    )

# --- Функция для создания адаптивной кнопки ---
def create_button(text):
    return Button(
        text=text,
        size_hint=(0.9, None),
        height=45
    )