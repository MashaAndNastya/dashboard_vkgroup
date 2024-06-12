import tkinter as tk
from tkinter import simpledialog, messagebox

from dash import dash


# Создаем главное окно Tkinter
root = tk.Tk()
root.withdraw()

dialog_options = {
    'title': 'Введите данные',
    'prompt': '',
    'background': '#736595',  # цвет фона
    'font': ('Montserrat', 12)  # шрифт и размер
}


def custom_dialog(prompt):
    dialog_options['prompt'] = prompt
    dialog = simpledialog._QueryString(root, **dialog_options)
    return dialog.result


# Запрашиваем токен и URL через всплывающее окно
access_token = simpledialog.askstring("Token", "Введите ваш токен:")
url_start = simpledialog.askstring("URL", "Введите URL:")

# Проверка на заполненность полей
if not access_token or not url_start:
    messagebox.showwarning("Ошибка", "Необходимо ввести токен и URL для запуска приложения!")

app = dash.Dash(__name__)

url = url_start.split('/')
domain = url[-1]
