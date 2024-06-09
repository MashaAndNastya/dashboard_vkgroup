import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from data import *
from datetime import date, datetime, timedelta

# Функции из data.py
start_time = '1709251200'
end_time = str(int(datetime.now().timestamp()))


def fetch_vk_stats(start_time, end_time, access_token, id_group):
    # Загрузка всех параметров
    params = {
        'access_token': access_token,
        'group_id': id_group,
        'timestamp_from': start_time,
        'timestamp_to': end_time,
        'v': version
    }

    # Запрос к апи
    response = requests.get('https://api.vk.com/method/stats.get', params=params)

    response_data = response.json()['response']

    # Инициализация заготовок
    likes, copies, hidden, comment, subscribed, unsubscribed, reach1, reach_subscribers, reach_unique_user = [], [], [], [], [], [], [], [], []
    sex_f, sex_m = [], []
    age_data = {}
    age_sex_data = {}

    for item in response_data:
        activity = item.get("activity", {})
        reach = item.get("reach", {})
        likes.append(activity.get("likes", 0))
        copies.append(activity.get("copies", 0))
        hidden.append(activity.get("hidden", 0))
        comment.append(activity.get("comment", 0))
        subscribed.append(activity.get("subscribed", 0))
        unsubscribed.append(activity.get("unsubscribed", 0))
        reach1.append(reach.get("reach", 0))
        reach_subscribers.append(reach.get("reach_subscribers", 0))
        reach_unique_user. append(reach1[-1]-reach_subscribers[-1])

        for sex in reach.get("sex", []):
            if sex["value"] == "f":
                sex_f.append(sex["count"])
            elif sex["value"] == "m":
                sex_m.append(sex["count"])

        for age_group in reach.get("age", []):
            age_data[age_group["value"]] = age_group["count"]

        for sex_age in reach.get("sex_age", []):
            age_sex_data[sex_age["value"]] = sex_age["count"]

    sex_df = pd.DataFrame({"f": sex_f, "m": sex_m})
    age_df = pd.DataFrame(list(age_data.items()), columns=["age_group", "count"])
    age_sex_df = pd.DataFrame(list(age_sex_data.items()), columns=["sex_age", "count"])
    return (likes, copies, hidden, comment, subscribed, unsubscribed, reach1, reach_subscribers, reach_unique_user,
            sex_df, age_df, age_sex_df)


# Перевод во временной промежуток(список) для построения графика
date_range = pd.date_range(start=pd.to_datetime(int(start_time), unit='s').date(), end=pd.to_datetime(int(end_time), unit='s').date())

# Вызов функции, запись  в переменные и постобработка данных
likes, copies, hidden, comment, subscribed, unsubscribed, reach, reach_subscribers, reach_unique_user, sex_df, age_df, age_sex_df = fetch_vk_stats(start_time, end_time, access_token, id_group)
count_female = sum(sex_df['f'])
count_male = sum(sex_df['m'])

# Данные для диаграммы возрастов
age_12_21 = age_df[(age_df['age_group'] == '12-18')]['count'].values[0]+age_df[(age_df['age_group'] == '18-21')]['count'].values[0]
age_21_27 = age_df[(age_df['age_group'] == '21-24')]['count'].values[0]+age_df[(age_df['age_group'] == '24-27')]['count'].values[0]
age_27_30 = age_df[(age_df['age_group'] == '27-30')]['count'].values[0]+age_df[(age_df['age_group'] == '30-35')]['count'].values[0]
age_35_45 = age_df[(age_df['age_group'] == '35-45')]['count'].values[0]
age_45_100 = age_df[(age_df['age_group'] == '45-100')]['count'].values[0]


# Расчёт ERR
def calculate_err_mean(likes, copies, comment, reach):
    err_mean_calculated = ((sum(likes) + sum(copies) + sum(comment)) / sum(reach)) * 100
    return err_mean_calculated


err_mean = calculate_err_mean(likes, copies, comment, reach)


def get_text_advice_err(err_mean):
    if err_mean <= 1:
        return "По общим стандартам ваш показатель ERR низкий."
    elif 1 < err_mean <= 3.5:
        return "По общим стандартам ваш показатель ERR средний, сложно сделать вывод об эффективности вашего сообщества."
    else:
        return "Поздравляем! По общим стандартам ваш показатель ERR высокий."


# Вычисление самого популярного поста
df = fetch_vk_data(access_token, version, count, offset)


def find_most_popular_post(df, start_time, end_time, like_weight=0.5, view_weight=0.3, comment_weight=0.2):
    # Преобразование столбца Date_UNIX в числовой тип данных
    df['Date_UNIX'] = pd.to_numeric(df['Date_UNIX'], errors='coerce')

    # Преобразование start_time и end_time из str в int
    start_time = int(start_time)
    end_time = int(end_time)

    # Преобразование даты из UNIX-времени в datetime
    df['Date'] = pd.to_datetime(df['Date_UNIX'], unit='s')

    # Фильтрация данных по промежутку времени
    filtered_df = df[(df['Date_UNIX'] >= start_time) & (df['Date_UNIX'] <= end_time)]

    # Вычисление популярности постов
    filtered_df.loc[:, 'Popularity'] = (
            df['Likes'] * like_weight + df['Views'] * view_weight + df['Comments'] * comment_weight
    )

    # Определение самого популярного поста
    most_popular_post = filtered_df.loc[filtered_df['Popularity'].idxmax()]

    return most_popular_post


most_popular_post = find_most_popular_post(df, start_time, end_time, like_weight=0.5, view_weight=0.3, comment_weight=0.2)


# Данные для div'ов

# Данные активности: лайки, комментарии, репосты
data_activity = {
    "Date": date_range,
    "Likes": likes,
    "Comments": comment,
    "Reposts": copies
}

# Построение dataframe для активности
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

# Построение dataframe для динамики
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
            html.P(err_mean),
            html.P(text_err),
            html.P('Советы:'),
            html.P(get_text_advice_err(err_mean))
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
    global start_time, end_time
    if selected_period == 'last_week':
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())
        filtered_df_activity = df_activity[df_activity['Unix'] >= start_time]
    elif selected_period == 'last_month':
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())
        filtered_df_activity = df_activity[df_activity['Unix'] >= start_time]
    elif selected_period == 'all_time':
        start_time = 1709286555
        filtered_df_activity = df_activity
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


#ERR
@app.callback(
    Output('ERR', 'children'),
    [Input('radio-items', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(selected_period, start_date, end_date):
        if selected_period == 'last_week':
            start_time_selected = int((datetime.now() - timedelta(days=7)).timestamp())
            end_time_selected = int(datetime.now().timestamp())
            # err_mean = 'text1'
        elif selected_period == 'last_month':
            start_time_selected = int((datetime.now() - timedelta(days=30)).timestamp())
            end_time_selected = int(datetime.now().timestamp())
            # err_mean = 'text2'
        elif selected_period == 'all_time':
            start_time_selected = 1709286555
            end_time_selected = int(datetime.now().timestamp())
            # err_mean = 'text3'
        elif selected_period == 'custom_date' and start_date and end_date:
            start_time_selected = int(datetime.fromisoformat(start_date).timestamp())
            end_time_selected = int(datetime.fromisoformat(end_date).timestamp())
            # err_mean = 'text4'

        data = fetch_vk_stats(start_time_selected, end_time_selected, access_token, id_group)
        likes_selected, copies_selected, comment_selected, reach_selected = data[0], data[1], data[3], data[6]

        err_mean_updated = calculate_err_mean(likes_selected, copies_selected, comment_selected, reach_selected)
        text_advice_err_updated = get_text_advice_err(err_mean_updated)

        return [
            html.P('ERR сообщества',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'font-family': 'Montserrat.ttf',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(err_mean_updated,
                   style={'color': '#f1986c',
                          'font-size': '34px',
                          'font-weight': 'bold',
                          'mardin-top': '5px',
                          'text-align': 'center'}
                   ),
            html.P(text_err,
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   ),
            html.P('Советы:',
                   style={'color': '#f9f9f9',
                          'font-size': '20px',
                          'font-weight': 'bold'}
                   ),

            html.P(text_advice_err_updated,
                   style={'color': '#f9f9f9', 'font-size': '12px'}),

            html.P(
                """Однако общие стандарты бывают обманчивы, лучший способ оценить
                привлекательность контента — ежемесячно сравнивать текущее значение с ER за предыдущий период.""",
                   style={'color': '#f9f9f9', 'font-size': '12px'}),
            html.P(
                "Можете воспользоваться следующими советами для повышения ERR:",
                   style={'color': '#f9f9f9', 'font-size': '12px'}),
            html.Ul([
                html.Li(
                    "Задавайте вопросы: это увеличивает количество комментариев.",
                        style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Вводите геймификацию: интерактивы удерживают людей и продлевают взаимодействие с публикацией.",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Проводите опросы и голосования: они хорошо вовлекают.",
                        style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Общайтесь в комментариях: отвечайте на сообщения — так люди будут втягиваться в общение с брендом.",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Оптимизируйте базу подписчиков.",
                        style={'color': '#f9f9f9', 'font-size': '12px'}),
            ])
        ]



# User_dynamic
@app.callback(
    Output('users_dynamic', 'figure'),
    [Input('radio-items', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')]
)
def update_graph(selected_period, start_date, end_date):
    global start_time, end_time
    if selected_period == 'last_week':
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())

    elif selected_period == 'last_month':
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())

    elif selected_period == 'all_time':
        start_time = 1709286555

    elif selected_period == 'custom_date' and start_date and end_date:
        start_time = int(datetime.fromisoformat(start_date).timestamp())
        end_time = int(datetime.fromisoformat(end_date).timestamp())

    fig_dynamic = go.Figure()
    fig_dynamic.add_trace(go.Scatter(x=df_dynamic['Date'], y=df_dynamic['Reach subscribers'], mode='lines+markers', name='Reach subscribers'))
    fig_dynamic.add_trace(go.Scatter(x=df_dynamic['Date'], y=df_dynamic['Reach unique'], mode='lines+markers', name='Reach unique'))

    fig_dynamic.update_layout(title='User Dynamics', xaxis_title='Date', yaxis_title='Count')
    fig_dynamic.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

    return fig_dynamic


if __name__ == '__main__':
    app.run_server(debug=True)

