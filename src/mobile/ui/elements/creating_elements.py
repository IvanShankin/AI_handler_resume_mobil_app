# --- Функция для создания "красивого" ввода ---
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp, sp


def create_textinput(hint, password=False, height=dp(40)):
    return TextInput(
        hint_text=hint,
        multiline=False,
        password=password,
        size_hint=(0.9, None),
        height=height,
        padding_y=(dp(5), dp(5))
    )

# --- Функция для создания адаптивной кнопки ---
def create_button(text, height=dp(40)):
    return Button(
        text=text,
        size_hint=(0.9, None),
        height=height
    )
