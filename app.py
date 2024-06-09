import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from data import *
from datetime import date, datetime, timedelta

# Данные активности: лайки, комментарии, репосты
data_activity = {
    "Date": date_range,
    "Likes": likes,
    "Comments": comment,
    "Reposts": copies
}

df_activity = pd.DataFrame(data_activity)
df_activity['Unix'] = df_activity['Date'].apply(lambda x: int(x.timestamp()))



# пример графика активности
fig_activity = go.Figure()
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Likes'], mode='lines+markers', name='Likes'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Comments'], mode='lines+markers', name='Comments'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Reposts'], mode='lines+markers', name='Reposts'))
fig_activity.update_layout(title='Activity', xaxis_title='Date', yaxis_title='Count')
fig_activity.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

# основу dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([

        # поля ввода
        html.Div([

            # поле для ссылки
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

            # поле для токена
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


        # выбор периода
        html.Div([
            dcc.RadioItems(
                id='radio-items',
                options=[
                    {'label': 'Весь период', 'value': 'all_time'},
                    {'label': 'Последняя неделя', 'value': 'last_week'},
                    {'label': 'Последний месяц', 'value': 'last_month'},
                    #{'label': 'Выбрать дату', 'value': 'custom_date'}
                ],
                value='last_week'
            ),

            # календарь
            # html.Div(id='date-picker-div', style={'display': 'none'}, children=[
            #     dcc.DatePickerRange(
            #         id='date-picker-range',
            #         start_date=date.today(),
            #         end_date_placeholder_text='Выберите дату!'
            #     )
            # ]),

            html.Div(
                id='output-dates',
                children=[],
                style={'display': 'none'}
            )
        ],
        className='date_container', style={'grid-column': 'span 6'}),



        # график users_activity
        html.Div([
            dcc.Graph(
                id="users_activity",
                figure=fig_activity,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),

        ],
        className='grid-container',
        style={'background-color': '#8459822', 'display': 'grid', 'grid-template-columns': 'repeat(12, 1fr)',
               'grid-gap': '20px', 'padding': '20px'})
], style={'background-color': '#8284bd', 'width': '100%'})


# @app.callback(
#     Output('date-picker-div', 'style'),
#     Input('radio-items', 'value')
# )
# def toggle_date_picker(selected_value):
#     if selected_value == 'custom_date':
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}
#
#
# @app.callback(
#     Output('output-dates', 'children'),
#     Input('date-picker-range', 'start_date'),
#     Input('date-picker-range', 'end_date')
# )
# def update_output(start_date, end_date):
#     if start_date and end_date:
#
#         # Конвертация строковых дат в объекты datetime
#         start_time = datetime.fromisoformat(start_date)
#         end_time = datetime.fromisoformat(end_date)
#
#         # Преобразование в формат UNIX
#         start_time = int(start_time.timestamp())
#         end_time = int(end_time.timestamp())
#
#         return f'Вы выбрали от {start_time} до {end_time}'
#     return 'Пожалуйста, выберите диапазон дат'


@app.callback(
    Output('users_activity', 'figure'),
    [Input('radio-items', 'value'),

     ]
)
def update_graph(selected_period):
    df_activity['Date'] = pd.to_datetime(df_activity['Date'])

    int(datetime.strptime(str(date.today()), "%Y-%m-%d").timestamp())
    if selected_period == 'last_week':
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())
    elif selected_period == 'last_month':
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())
    elif selected_period == 'all_time':
        start_time = 1709286555


    # elif selected_period == 'custom_date' and start_date and end_date:
    #     start_date = datetime.fromisoformat(start_date).date()
    #     end_date = datetime.fromisoformat(end_date).date()
    #     filtered_df = df_activity[(df_activity['Date'] >= start_date) & (df_activity['Date'] <= end_date)]

    filtered_df_activity = df_activity[df_activity['Unix'] >= start_time]

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


if __name__ == '__main__':
    app.run_server(debug=True)

