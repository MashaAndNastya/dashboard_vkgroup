import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
import time
import pandas as pd
from datetime import datetime, timezone, date, timedelta
import webbrowser
import os
from threading import Timer

# Создаем главное окно Tkinter
root = tk.Tk()
root.withdraw()

# Запрашиваем токен и URL через всплывающее окно
access_token = simpledialog.askstring("Token", "Введите ваш токен:")
url_start = simpledialog.askstring("URL", "Введите URL:")

# Проверка на заполненность полей
if not access_token or not url_start:
    messagebox.showwarning("Ошибка", "Необходимо ввести токен и URL для запуска приложения!")



app = dash.Dash(__name__)

url = url_start.split('/')
domain = url[-1]
#получаем id группы через запрос
response = requests.get('https://api.vk.com/method/utils.resolveScreenName',
                        params={'access_token': access_token,
                                'screen_name': domain,
                                'v': 5.199})
id_group = response.json()['response']['object_id']


def fetch_vk_data(access_token, version = 5.199 , count = 100, offset = 0):

    data_dict = {
        'ID': [],
        'Text': [],
        'Likes': [],
        'Comments': [],
        'Views': [],
        'Reposts': [],
        'URL': [],
        'Date': [],
        'Date_UNIX': [],
        'Photo': []
    }


    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': access_token,
                                    'v': 5.199,
                                    'domain': domain,
                                    'count': count,
                                    'offset': offset})

    data_start = response.json()
    count_posts = data_start['response']['count']
    for i in range(0, count_posts, 100):
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={'access_token': access_token,
                                        'v': version,
                                        'domain': domain,
                                        'count': count,
                                        'offset': offset})
        data = response.json()['response']['items']
        offset += 100
        data_dict['ID'].extend([item['id'] for item in data])
        data_dict['Likes'].extend([item['likes']['count'] for item in data])
        data_dict['Text'].extend([item['text'] for item in data])
        data_dict['Comments'].extend([item['comments']['count'] for item in data])

        for item in data:
            if 'views' in item:
                data_dict['Views'].append(item['views']['count'])
            else:
                data_dict['Views'].append(None)
        data_dict['Reposts'].extend([item['reposts']['count'] for item in data])
        data_dict['URL'].extend([url_start + "?w=wall-" + str(id_group) + "_" + str(item['id']) for item in data])
        data_dict['Date'].extend([datetime.fromtimestamp(item['date'], timezone.utc).strftime('%Y-%m-%d') for item in data])
        data_dict['Date_UNIX'].extend([item['date'] for item in data])
        for item in data:
            if 'attachments' in item and item['attachments'] and item['attachments'][0]['type'] == 'photo':
                data_dict['Photo'].append(item['attachments'][0]['photo']['sizes'][-1]['url'])
            else:
                data_dict['Photo'].append("No photo")
        time.sleep(0.01)

    df_posts = pd.DataFrame(data_dict)
    return df_posts
# Парсинг постов
df = fetch_vk_data(access_token, version=5.199, count=100, offset=0)
# Начальное время
#start_time = df['Date_UNIX'].iloc[-1]+10000
start_time = '1672562957'
end_time = str(int(datetime.now().timestamp()))

def fetch_vk_stats(start_time, end_time, access_token, id_group):
    # Загрузка всех параметров
    params = {
        'access_token': access_token,
        'group_id': id_group,
        'timestamp_from': start_time,
        'timestamp_to': end_time,
        'v': 5.199
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


# Данные для пола
def get_sex(sex_df):
    count_female = sum(sex_df['f'])
    count_male = sum(sex_df['m'])
    return count_female, count_male
#топ-5 категорий по половозрастному составу
def top_5_age_sex_category(age_sex_df):
    age_sex_df = age_sex_df.sort_values(by=['count'], ascending=False)
    total_count = age_sex_df['count'].sum()
    top_5 = []
    for index, row in age_sex_df.iterrows():
        if row['count'] != 0 and len(top_5) < 5:
            sex, age = row['sex_age'].split(';')
            category = f"{ 'Мужчины' if sex == 'm' else 'Женщины' } {age} лет"
            percentage = round((row['count'] / total_count) * 100, 3)
            top_5.append((category, percentage))
    return top_5
top_5 = top_5_age_sex_category(age_sex_df)
# Данные для диаграммы возрастов
def get_age(age_df):
    age_12_21 = age_df[(age_df['age_group'] == '12-18')]['count'].values[0]+age_df[(age_df['age_group'] == '18-21')]['count'].values[0]
    age_21_27 = age_df[(age_df['age_group'] == '21-24')]['count'].values[0]+age_df[(age_df['age_group'] == '24-27')]['count'].values[0]
    age_27_30 = age_df[(age_df['age_group'] == '27-30')]['count'].values[0]+age_df[(age_df['age_group'] == '30-35')]['count'].values[0]
    age_35_45 = age_df[(age_df['age_group'] == '35-45')]['count'].values[0]
    age_45_100 = age_df[(age_df['age_group'] == '45-100')]['count'].values[0]

    return age_12_21, age_21_27, age_27_30, age_35_45, age_45_100


# Расчёт ERR
def calculate_err_mean(likes, copies, comment, reach):
    err_mean_calculated = ((sum(likes) + sum(copies) + sum(comment)) / sum(reach)) * 100
    return err_mean_calculated


err_mean = calculate_err_mean(likes, copies, comment, reach)


# Советы по повышению ERR
def get_text_advice_err(err_mean):
    if err_mean <= 1:
        return "По общим стандартам ваш показатель ERR низкий."
    elif 1 < err_mean <= 3.5:
        return "По общим стандартам ваш показатель ERR средний, сложно сделать вывод об эффективности вашего сообщества."
    else:
        return "Поздравляем! По общим стандартам ваш показатель ERR высокий."


# Расчёт AR
def calculate_ar_mean(copies, reach):
    ar_mean_calculated = (sum(copies) / sum(reach)) * 100
    return ar_mean_calculated


ar_mean = calculate_ar_mean(copies, reach)


# Советы по повышению AR
def get_text_advice_ar(ar_mean):
    if ar_mean <= 1:
        return "По общим стандартам ваш показатель AR низкий."
    elif 1 < ar_mean <= 5:
        return "По общим стандартам ваш показатель AR средний, сложно сделать вывод об эффективности вашего сообщества."
    else:
        return "Поздравляем! По общим стандартам ваш показатель AR высокий."



#вычисление самого популярного поста
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
text_err = 'Коэффициент охвата (Engagement Rate by Reach) — метрика, которая показывает, сколько людей из тех, что увидели пост, взаимодействовали с ним: комментировали, ставили лайки, делали репосты. Более правильно ERR переводится как коэффициент вовлечённости по охвату.Как рассчитать: (количество реакций / охват) × 100%'
text_ar = 'В переводе с английского amplification rate означает «скорость распространения». AR характеризует виральность, то есть показывает, понравилась ли публикация подписчикам, и готовы ли они поделиться ей на своей странице. Чем выше коэффициент распространения, тем больше шансов, что пост быстро разойдется по соцсети. Как рассчитать: (количество комментрариев / охват) × 100%'

# Пол для круговой диаграммы
gender_list = list(get_sex(sex_df))

# Возраст для круговой диаграммы
age_list = list(get_age(age_df))

#подготовка списка категорий целевой аудитории к выводу на экран
list_items = ""
for entry in top_5:
    list_items += f"<li style='color: #f9f9f9; font-size: 16px;'>{entry[0]} - {entry[1]:.3f}%</li>\n"

text_target_audience = """
Этот элемент дашборда поможет вам сделать выводы о вашей целевой аудитории. 
Исходя из этих данных, вы сможете регулировать и корректировать свой контент, закупать таргетированную рекламу и развивать своё сообщество в соответствии с вашими целями.
"""



# # HTML шаблон страницы
# app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([

        # Поля ввода контейнер
        html.Div([

            # Поле для ссылки
            html.Div([
                html.P(['Ссылка на сообщество, по которому представлена статистика'],
                       className='link_header',
                       style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px'}),
                html.Div(url_start, id='link_display',
                         style={'width': '95%', 'padding': '10px', 'font-size': '18px', 'border-radius': '10px',
                                'border': '1px solid #ccc'}),
            ], className='row',
                style={'display': 'flex', 'flex-direction': 'column', 'margin-bottom': '10px',
                       'border-radius': '20px', }),

            # Поле для токена (с кнопкой)
            html.Div([
                html.P(['Токен, который вы ввели'],
                       className='token_header',
                       style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px'}),
                html.Div('Ваш_секретный_токен', id='token_display',
                         style={'width': '95%', 'padding': '10px', 'font-size': '18px', 'border-radius': '10px',
                                'border': '1px solid #ccc'}),
                html.Button('Показать токен', id='show_token_button', n_clicks=0,
                            style={"padding": "10px", "border-radius": "10px", "cursor": "pointer"})
            ], className='row', style={'display': 'flex', 'flex-direction': 'column', 'border-radius': '20px'}),
        ], className='fields_container', style={'grid-column': 'span 6'}),


        # Выбор периода
        html.Div([
            dcc.RadioItems(
                id='radio-items',
                options=[
                    {'label': 'Весь период', 'value': 'all_time'},
                    {'label': 'Последняя неделя', 'value': 'last_week'},
                    {'label': 'Последний месяц', 'value': 'last_month'},
                    {'label': 'Выбрать дату', 'value': 'custom_date'},
                ],
                value='all_time',
                inputClassName='radio-item-container',
                style={'margin-bottom': '20px'}
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

        # Круговая диаграмма М/Ж
        html.Div([
            dcc.Graph(
                id="gender-graph",
                figure=px.pie(
                    values=gender_list,
                    labels=['Male', 'Female'],
                    title='Пол'
                ).update_traces(insidetextorientation='radial'),
                className='dcc_compon'
            )
        ], id='gender',
            style={'grid-column': 'span 3', 'padding': '10px', 'border-radius': '5px', 'background-color': '#39344a'}),

        # Самый популярный пост
        html.Div([
            html.P('Самый популярный пост', style={'color': '#FFFFFF', 'fontWeight': 'bold', 'fontSize': '20px'}),
            html.Img(src=most_popular_post['Photo'], style={'max-width': '100%', 'border-radius': '5px'}),
            html.P(most_popular_post['Text'], style={'color': '#FFFFFF', 'margin-top': '10px'}),
            html.P(
                f"👍 {most_popular_post['Likes']}   💬 {most_popular_post['Comments']}   👀 {most_popular_post['Views']}   🔄 {most_popular_post['Reposts']}",
                style={'color': '#FFFFFF', 'margin-top': '10px'}),
            html.A('Ссылка на пост', href=most_popular_post['URL'], target='_blank',
                   style={'color': '#1DA1F2', 'margin-top': '10px', 'textDecoration': 'none'})
        ], id='post',
            className='post-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'padding': '20px'}),

        # График users_dynamic
        html.Div([
            dcc.Graph(
                id="users_dynamic",
                figure=fig_dynamic,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),

        # Круговая диаграмма возраст
        html.Div([
            dcc.Graph(
                id="age-graph",
                figure=px.pie(
                    values=age_list,
                    names=['12-21', '21-27', '27-30', '30-45', '45-100'],
                    title='Возраст'
                ),
                className='dcc_compon'
            )
        ], id='age',
            style={'grid-column': 'span 3', 'padding': '10px', 'border-radius': '5px', 'background-color': '#39344a'}),

        # Топ целевой аудитории
        html.Div([
            html.P("Основные категории целевой аудитории", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            html.P(text_target_audience, style={'color': '#f9f9f9', 'font-size': '16px'}),
            html.Ol(
                children=dcc.Markdown(list_items, dangerously_allow_html=True)
                # Добавляем элементы списка, обработанные как HTML
            )
        ], id ='target_audience', className='text-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column', 'padding': '20px'}),

        # ERR сообщества
        html.Div([
            html.P('ERR сообщества'),
            html.P(err_mean),
            html.P(text_err),
            html.P('Советы:'),
            html.P(get_text_advice_err(err_mean))
        ], id='ERR',
            className='text-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 6',
                   'display': 'flex', 'flex-direction': 'column', 'padding': '20px'}),

        # AR сообщества
        html.Div([
            html.P('AR сообщества'),
            html.P(text_ar),
            html.P('Советы:'),
            html.P(get_text_advice_ar(ar_mean))
        ], id='AR',
            className='text-container',
            style={'background-color': '#39344a', 'padding': '20px', 'border-radius': '5px', 'grid-column': 'span 6',
                   'display': 'flex', 'flex-direction': 'column'}),

    ],
        className='grid-container',
        style={'background-color': '#8459822', 'display': 'grid', 'grid-template-columns': 'repeat(12, 1fr)',
               'grid-gap': '20px', 'padding': '20px'})

], style={'background-color': '#8284bd', 'width': '100%'})

# Коллбэк для показа или сокрытия токена
# Коллбэк для показа или сокрытия токена
@app.callback(
    Output('token_display', 'children'),
    [Input('show_token_button', 'n_clicks')],
    [State('show_token_button', 'children')],
    prevent_initial_call=True
)
def toggle_token(n_clicks, button_text):
    if button_text == 'Показать токен':
        return access_token
    else:
        return '******'
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
# Users_activity & Users_dynamic

@app.callback(
    [Output('users_activity', 'figure'),
     Output('users_dynamic', 'figure')],
    [Input('radio-items', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(selected_period, start_date, end_date):
    # Инициализация временных промежутков
    start_time = None
    end_time = None

    # Установка временных промежутков в зависимости от выбранного периода
    if selected_period == 'last_week':
        start_time = int((datetime.now() - timedelta(days=7)).timestamp())
        end_time = int(datetime.now().timestamp())
    elif selected_period == 'last_month':
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())
        end_time = int(datetime.now().timestamp())
    elif selected_period == 'all_time':
        start_time = 1709286555
        end_time = int(datetime.now().timestamp())
    elif selected_period == 'custom_date' and start_date and end_date:
        start_time = int(datetime.fromisoformat(start_date).timestamp())
        end_time = int(datetime.fromisoformat(end_date).timestamp())

    # Проверка, что временные промежутки были установлены корректно
    if start_time is None or end_time is None:
        return go.Figure(), go.Figure()  # Возвращаем пустые фигуры в случае ошибки

    # Фильтрация данных по временным промежуткам
    filtered_df_activity = df_activity[(df_activity['Unix'] >= start_time) & (df_activity['Unix'] <= end_time)]
    filtered_df_dynamic = df_dynamic[(df_dynamic['Unix'] >= start_time) & (df_dynamic['Unix'] <= end_time)]

    # Обновленные данные для активности пользователей
    fig_activity = go.Figure()
    fig_activity.add_trace(
        go.Scatter(x=filtered_df_activity['Date'], y=filtered_df_activity['Likes'], mode='lines+markers', name='Лайки'))
    fig_activity.add_trace(
        go.Scatter(x=filtered_df_activity['Date'], y=filtered_df_activity['Comments'], mode='lines+markers', name='Комментарии'))
    fig_activity.add_trace(
        go.Scatter(x=filtered_df_activity['Date'], y=filtered_df_activity['Reposts'], mode='lines+markers', name='Репосты'))

    # Обновленный график активности пользователей
    fig_activity.update_layout(title='Aктивность пользователей', xaxis_title='Дата', yaxis_title='Количество')
    fig_activity.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

    # Обновленные данные для динамики пользователей
    fig_dynamic = go.Figure()
    fig_dynamic.add_trace(go.Scatter(x=filtered_df_dynamic['Date'], y=filtered_df_dynamic['Reach subscribers'], mode='lines+markers', name='Охваты по подписчикам'))
    fig_dynamic.add_trace(go.Scatter(x=filtered_df_dynamic['Date'], y=filtered_df_dynamic['Reach unique'], mode='lines+markers', name='Уникальные охваты'))

    # Обновленный график динамики пользователей
    fig_dynamic.update_layout(title='Динамика охватов', xaxis_title='Дата', yaxis_title='Количество')
    fig_dynamic.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

    return fig_activity, fig_dynamic


#ERR, AR, gender & age pie graphs, most popular post
@app.callback(
    [Output('ERR', 'children'),
     Output('AR', 'children'),
     Output('gender-graph', 'figure'),
     Output('age-graph', 'figure'),
     Output('post', 'children'),
     Output('target_audience', 'children')],
    [Input('radio-items', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(selected_period, start_date, end_date):
        # Инициализация переменных по умолчанию
        start_time_selected = None
        end_time_selected = None
        if selected_period == 'last_week':
            start_time_selected = int((datetime.now() - timedelta(days=7)).timestamp())
            end_time_selected = int(datetime.now().timestamp())
        elif selected_period == 'last_month':
            start_time_selected = int((datetime.now() - timedelta(days=30)).timestamp())
            end_time_selected = int(datetime.now().timestamp())
        elif selected_period == 'all_time':
            start_time_selected = 1709286555
            end_time_selected = int(datetime.now().timestamp())
        elif selected_period == 'custom_date' and start_date and end_date:
            start_time_selected = int(datetime.fromisoformat(start_date).timestamp())
            end_time_selected = int(datetime.fromisoformat(end_date).timestamp())

        # Получаем новые данные с учетом выбранного промежутка времени
        data = fetch_vk_stats(start_time_selected, end_time_selected, access_token, id_group)

        # Собираем нужные данные для ERR & AR
        likes_selected, copies_selected, comment_selected, reach_selected = data[0], data[1], data[3], data[6]

        # Обновляем ERR
        err_mean_updated = calculate_err_mean(likes_selected, copies_selected, comment_selected, reach_selected)
        text_advice_err_updated = get_text_advice_err(err_mean_updated)

        # Обновляем AR
        ar_mean_updated = calculate_ar_mean(copies_selected, reach_selected)
        text_advice_ar_updated = get_text_advice_ar(ar_mean_updated)

        # Обновляем данные для gender
        sex_df_selected = data[9]
        gender_list_updated = list(get_sex(sex_df_selected))

        # Обновляем pie chart для gender
        gender_pie_updated = px.pie(
            values=gender_list_updated,
            names=['Male', 'Female'],
            title='Пол'
        ).update_layout(
            legend_orientation='h',
            title_x=0.5,
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )

        # Обновляем данные для age
        age_df_selected = data[10]
        age_list_updated = list(get_age(age_df_selected))

        # Обновляем pie chart для age
        age_pie_updated = px.pie(
            values=age_list_updated,
            names=['12-21', '21-27', '27-30', '30-45', '45-100'],
            title='Возраст'
        ).update_layout(
            legend_orientation='h',
            title_x=0.5,
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        # Обновляем самый популярный пост
        most_popular_post_updated = find_most_popular_post(df, start_time_selected, end_time_selected, like_weight=0.5, view_weight=0.3, comment_weight=0.2)
        post_card_updated = [
            html.P('Самый популярный пост', style={'color': '#FFFFFF', 'fontWeight': 'bold', 'fontSize': '20px'}),
            html.Img(src=most_popular_post_updated['Photo'], style={'max-width': '100%', 'border-radius': '5px'}),
            html.P(most_popular_post_updated['Text'], style={'color': '#FFFFFF', 'margin-top': '10px'}),
            html.P(
                f"👍 {most_popular_post_updated['Likes']}   💬 {most_popular_post_updated['Comments']}   👀 {most_popular_post_updated['Views']}   🔄 {most_popular_post_updated['Reposts']}",
                style={'color': '#FFFFFF', 'margin-top': '10px'}
            ),
            html.A('Ссылка на пост', href=most_popular_post_updated['URL'], target='_blank',
                   style={'color': '#1DA1F2', 'margin-top': '10px', 'textDecoration': 'none'})
        ]
        #Обновляем целевую аудиторию
        age_sex_df_selected = data[11]
        top_5_updated = top_5_age_sex_category(age_sex_df_selected)
        list_items_updated = ""
        for entry in top_5_updated:
            list_items_updated += f"<li style='color: #f9f9f9; font-size: 16px;'>{entry[0]} - {entry[1]:.3f}%</li>\n"

        # Возвращаем ERR, gender pie chart, age pie chart, самый популярный пост, целевую аудиторию
        return ([
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
        ],
        [
            html.P('AR сообщества',
                   style={'color': '#f9f9f9',
                          'font-size': '24px',
                          'font-weight': 'bold',
                          'font-family': 'Montserrat.ttf',
                          'mardin-bottom': '5px',
                          'text-align': 'center'}
                   ),
            html.P(ar_mean_updated,
                   style={'color': '#f1986c',
                          'font-size': '34px',
                          'font-weight': 'bold',
                          'mardin-top': '5px',
                          'text-align': 'center'}
                   ),
            html.P(text_ar,
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   ),
            html.P('Советы:',
                   style={'color': '#f9f9f9',
                          'font-size': '20px',
                          'font-weight': 'bold'}
                   ),

            html.P(text_advice_ar_updated,
                   style={'color': '#f9f9f9', 'font-size': '12px'}),

            html.P(
                """Однако общие стандарты бывают обманчивы, лучший способ оценить
                привлекательность контента — ежемесячно сравнивать текущее значение с AR за предыдущий период.""",
                style={'color': '#f9f9f9', 'font-size': '12px'}),
            html.P(
                "Можете воспользоваться следующими советами для повышения AR:",
                style={'color': '#f9f9f9', 'font-size': '12px'}),
            html.Ul([
                html.Li(
                    "Размещайте больше полезных информативных постов. Подписчики должны видеть: вы — настоящий профессионал в своей области и вашему мнению можно доверять. ",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Публикуйте разнообразный контент. Чередуйте информационные посты с вовлекающими и развлекательными публикациями.",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Добавляйте в контент-план форматы, которые репостят чаще других (чек-листы, гайды, подборки, карточки). Устраивайте конкурсы и розыгрыши среди подписчиков. ",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Анализируйте контент конкурентов. Посмотрите, какими записями пользователи делятся чаще всего, в каком ключе поданы самые популярные посты, в каком стиле написаны тексты и какие изображения использованы: реальные фотографии, коллажи или мемы.",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
                html.Li(
                    "Экспериментируйте со временем публикации постов. К примеру, пользователи соцсети «ВКонтакте» проявляют самую большую активность с 8:00 до 10:00 (в это время подписчики готовятся к учебе и работе, они с удовольствием почитают легкие развлекательные посты). Следующий период активности — с 12:00 до 15:00 (сейчас можно публиковать серьезные материалы: обзоры товаров, презентации новых продуктов, результаты исследований). Время максимального охвата — с 21:00 до 23:00. Для этого интервала оставьте самые важные и интересные новости: информацию об акциях и скидках, новостях компании.",
                    style={'color': '#f9f9f9', 'font-size': '12px'}),
            ])
        ], gender_pie_updated, age_pie_updated, post_card_updated,
                [
                    html.P("Основные категории целевой аудитории", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
                    html.P(text_target_audience, style={'color': '#f9f9f9', 'font-size': '16px'}),
                    html.Ol(children=dcc.Markdown(list_items_updated, dangerously_allow_html=True))
                ]
        )



def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')
if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=1222)








