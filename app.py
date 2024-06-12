import webbrowser
import os
from threading import Timer
from dialog_window import app
from layout import app_layout

app.layout = app_layout


def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')


if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=1222)
