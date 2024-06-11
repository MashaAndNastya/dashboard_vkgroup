import dash
from dash import html, dcc

# Создание приложения Dash
app = dash.Dash(__name__, external_stylesheets=['style.css'])

# Определение макета страницы для регистрации
app.layout = html.Div([
    html.H1('Регистрация пользователя'),
    html.Label('Введите URL адрес:'),
    dcc.Input(id='url-input', type='text'),
    html.Label('Введите токен:'),
    dcc.Input(id='token-input', type='text'),
    html.Button('Зарегистрироваться', id='submit-button'),
])

# Обработка данных, переданных пользователем
@app.callback(
    dash.dependencies.Output('url-output', 'children'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('url-input', 'value'),
     dash.dependencies.State('token-input', 'value')]
)
def update_output(n_clicks, url_input, token_input):
    if n_clicks is not None:
        # Сохранение данных в отдельные переменные
        url = url_input
        token = token_input
        # Передача данных в приложение
        # Например, вызов функции или метода для обработки данных

# Запуск приложения Dash
if __name__ == '__main__':
    app.run_server(debug=True)