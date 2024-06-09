import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from data import *
from datetime import date, datetime, timedelta

# Данные для div'ов

# Данные активности: лайки, комментарии, репосты
data_activity = {
    "Date": date_range,
    "Likes": likes,
    "Comments": comment,
    "Reposts": copies
}

df_activity = pd.DataFrame(data_activity)
df_activity['Unix'] = df_activity['Date'].apply(lambda x: int(x.timestamp()))

# Построение графика активности
fig_activity = go.Figure()
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Likes'], mode='lines+markers', name='Likes'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Comments'], mode='lines+markers', name='Comments'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Reposts'], mode='lines+markers', name='Reposts'))
fig_activity.update_layout(title='Activity', xaxis_title='Date', yaxis_title='Count')
fig_activity.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')


# Данные динамики пользователей: просмотры, подписки
data_dynamic = {
    "Date": date_range,
    "Reach subscribers":  reach_subscribers,
    "Reach unique": reach_unique_user
}

df_dynamic = pd.DataFrame(data_dynamic)
df_dynamic['Unix'] = df_dynamic['Date'].apply(lambda x: int(x.timestamp()))

# Построение графика динамики пользователей
fig_dynamic = go.Figure()
fig_dynamic.add_trace(go.Scatter(x=df_dynamic['Date'], y=df_dynamic['Reach subscribers'], mode='lines+markers', name='Reach subscribers'))
fig_dynamic.add_trace(go.Scatter(x=df_dynamic['Date'], y=df_dynamic['Reach unique'], mode='lines+markers', name='Reach unique'))
fig_dynamic.update_layout(title='User Dynamics', xaxis_title='Date', yaxis_title='Count')
fig_dynamic.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

# Текстовые данные
text_err = 'Коэффициент охвата (Engagement Rate by Reach) — метрика, которая показывает, сколько людей из тех, что увидели пост, взаимодействовали с ним: комментировали, ставили лайки, делали репосты. Более правильно ERR переводится как коэффициент вовлечённости по охвату.\nКак рассчитать: количество реакций / охват × 100%'
text_arr = 'Annual Recurring Revenue (ARR) — это регулярный ежегодный доход. \nКак расчитать: Количество клиентов * Средний доход с клиента в месяц'

# Еще какие-то данные
text1_err = err_mean
text1_arr = 'Text 1 ARR'
text1_other = 'Text 1 OTHER'
header1 = 'Header 1'
photo1 = 'Photo 1'
gender1 = [count_female, count_male]
age1 = [age_12_21, age_21_27, age_27_30, age_35_45, age_45_100]


# HTML шаблон страницы
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([

        # Поля ввода контейнер
        html.Div([

            # Поле для ссылки
            html.Div([
                html.P(['Введите ссылку на сообщество'],
                        className='link_header', style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px'}),
                dcc.Textarea(
                    id='link_textarea',
                    placeholder='Ссылка на сообщество',
                    style={'width': '95%', 'height': '20px', 'padding': '10px', 'font-size': '18px', 'border-radius': '10px', 'resize': 'none', 'overflow': 'hidden'},
                    className='link_textarea',
                )
            ], className='row',
                style={'display': 'flex', 'flex-direction': 'column', 'margin-bottom': '10px', 'border-radius': '20px',}),

            # Поле для токена
            html.Div([
                html.P(['Введите Ваш токен'],
                        className='token_header', style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px'}),
                dcc.Textarea(
                    id='token_textarea',
                    placeholder='Ваш токен',
                    style={'width': '95%', 'height': '20px', 'padding': '10px', 'font-size': '18px', 'border-radius': '10px', 'resize': 'none', 'overflow': 'hidden'},
                    className='token_textarea',
                )
            ], className='row',
                style={'display': 'flex', 'flex-direction': 'column', 'border-radius': '20px'}),

        ], className='fields_container', style={'grid-column': 'span 6'}),


        # Выбор периода
        html.Div([
            dcc.RadioItems(
                id='radio-items',
                options=[
                    {'label': 'Весь период', 'value': 'all_time'},
                    {'label': 'Последняя неделя', 'value': 'last_week'},
                    {'label': 'Последний месяц', 'value': 'last_month'},
                    {'label': 'Выбрать дату', 'value': 'custom_date'}
                ],
                value='all_time'
            ),

            # Календарь
            html.Div(
                id='date-picker-div',
                style={'display': 'none'},
                children=[
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=date.today(),
                    end_date_placeholder_text='Выберите дату!'
                )
            ]),

            html.Div(
                id='output-dates',
                children=[],
                style={'display': 'none'}
            )
        ],
        className='date_container', style={'grid-column': 'span 6'}),


        # График users_activity
        html.Div([
            dcc.Graph(
                id="users_activity",
                figure=fig_activity,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),

        # ERR сообщества
        html.Div([
            html.P('ERR сообщества'),
            html.P(text1_err),
            html.P(text_err),
            html.P('Советы:'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='ERR',
            className='text-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column', 'padding': '20px'}),

        # Самый популярный пост
        html.Div([
            html.P('Самый популярный пост'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='post',
            className='post-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column',  'align-items': 'center', 'padding': '20px'}),


        # График users_dynamic
        html.Div([
            dcc.Graph(
                id="users_dynamic",
                figure=fig_dynamic,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),

        # AR сообщества
        html.Div([
            html.P('AR сообщества'),
            html.P(text1_arr),
            html.P(text_arr),
            html.P('Советы:'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='ARR',
            className='text-container',
            style={'background-color': '#39344a', 'padding': '20px', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column'}),


        # Какие-то еще метрики
        html.Div([
            html.H6("Random Text Container 1", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            html.P(text1_other)
        ], className='text-container',
            style={'background-color': '#333333', 'padding': '20px', 'border-radius': '5px', 'grid-column': 'span 3'}),


        # Круговая диаграмма М/Ж
        html.Div([
            dcc.Graph(
                id="gender-graph",
                figure=px.pie(
                    values=gender1,
                    labels=['Male', 'Female'],
                    title='Пол'
                ).update_traces(insidetextorientation='radial'),
                className='dcc_compon'
            )
        ], id='gender',
            style={'grid-column': 'span 3', 'padding': '10px', 'border-radius': '5px', 'background-color': '#39344a'}),


        # Круговая диаграмма возраст
        html.Div([
            dcc.Graph(
                id="age-graph",
                figure=px.pie(
                    values=age1,
                    names=['12-21', '21-27', '27-30', '30-45', '45-100'],
                    title='Возраст'
                ),
                className='dcc_compon'
            )
        ], id='age',
            style={'grid-column': 'span 3', 'padding': '10px', 'border-radius': '5px', 'background-color': '#39344a'})

    ],
        className='grid-container',
        style={'background-color': '#8459822', 'display': 'grid', 'grid-template-columns': 'repeat(12, 1fr)',
               'grid-gap': '20px', 'padding': '20px'})

], style={'background-color': '#8284bd', 'width': '100%'})


# Открытие custom_date поля
@app.callback(
    Output('date-picker-div', 'style'),
    Input('radio-items', 'value')
)
def toggle_date_picker(selected_value):
    if selected_value == 'custom_date':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# Output_dates (даты из custom_dates)
@app.callback(
    Output('output-dates', 'children'),
    [Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')]
)
def update_output(start_date, end_date):
    if start_date and end_date:
        # Преобразование в формат UNIX
        start_time = int(datetime.fromisoformat(start_date).timestamp())
        end_time = int(datetime.fromisoformat(end_date).timestamp())

        return f'Вы выбрали от {start_time} до {end_time}'
    return 'Пожалуйста, выберите диапазон дат'


# User_activity
@app.callback(
    Output('users_activity', 'figure'),
    [Input('radio-items', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')]
)
def update_graph(selected_period, start_date, end_date):
    df_activity['Date'] = pd.to_datetime(df_activity['Date'])

    filtered_df_activity = df_activity.copy()

    int(datetime.strptime(str(date.today()), "%Y-%m-%d").timestamp())
    if selected_period == 'last_week':
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())
        filtered_df_activity = df_activity[df_activity['Unix'] >= start_time]

    elif selected_period == 'last_month':
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())
        filtered_df_activity = df_activity[df_activity['Unix'] >= start_time]

    elif selected_period == 'all_time':
        start_time = 1709286555
        filtered_df_activity = df_activity[df_activity['Unix'] >= start_time]

    elif selected_period == 'custom_date' and start_date and end_date:
        start_time = int(datetime.fromisoformat(start_date).timestamp())
        end_time = int(datetime.fromisoformat(end_date).timestamp())
        filtered_df_activity = df_activity[(df_activity['Unix'] >= start_time) & (df_activity['Unix'] <= end_time)]

    fig_activity = go.Figure()
    fig_activity.add_trace(
        go.Scatter(x=filtered_df_activity['Date'], y=filtered_df_activity['Likes'], mode='lines+markers', name='Likes'))
    fig_activity.add_trace(
        go.Scatter(x=filtered_df_activity['Date'], y=filtered_df_activity['Comments'], mode='lines+markers', name='Comments'))
    fig_activity.add_trace(
        go.Scatter(x=filtered_df_activity['Date'], y=filtered_df_activity['Reposts'], mode='lines+markers', name='Reposts'))

    fig_activity.update_layout(title='Activity', xaxis_title='Date', yaxis_title='Count')
    fig_activity.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

    return fig_activity


# User_dynamic
@app.callback(
    Output('users_dynamic', 'figure'),
    [Input('radio-items', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')]
)
def update_graph(selected_period, start_date, end_date):
    df_dynamic['Date'] = pd.to_datetime(df_dynamic['Date'])

    filtered_df_dynamic = df_dynamic.copy()

    int(datetime.strptime(str(date.today()), "%Y-%m-%d").timestamp())
    if selected_period == 'last_week':
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())
        filtered_df_dynamic = df_dynamic[df_dynamic['Unix'] >= start_time]

    elif selected_period == 'last_month':
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())
        filtered_df_dynamic = df_dynamic[df_dynamic['Unix'] >= start_time]

    elif selected_period == 'all_time':
        start_time = 1709286555
        filtered_df_dynamic = df_dynamic[df_dynamic['Unix'] >= start_time]

    elif selected_period == 'custom_date' and start_date and end_date:
        start_time = int(datetime.fromisoformat(start_date).timestamp())
        end_time = int(datetime.fromisoformat(end_date).timestamp())
        filtered_df_dynamic = df_dynamic[(df_dynamic['Unix'] >= start_time) & (df_dynamic['Unix'] <= end_time)]

    fig_dynamic = go.Figure()
    fig_dynamic.add_trace(go.Scatter(x=filtered_df_dynamic['Date'], y=filtered_df_dynamic['Reach subscribers'], mode='lines+markers', name='Reach subscribers'))
    fig_dynamic.add_trace(go.Scatter(x=filtered_df_dynamic['Date'], y=filtered_df_dynamic['Reach unique'], mode='lines+markers', name='Reach unique'))

    fig_dynamic.update_layout(title='User Dynamics', xaxis_title='Date', yaxis_title='Count')
    fig_dynamic.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

    return fig_dynamic
if __name__ == '__main__':
    app.run_server(debug=True)

