from datetime import date
from dialog_window import app, url_start
from items_data import fig_activity, gender_list, most_popular_post, age_list, fig_dynamic, list_items, err_mean, ar_mean
from datetime import datetime, timedelta
import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dialog_window import access_token
from get_data import fetch_vk_stats, id_group, df
from items_data import df_activity, df_dynamic, calculate_err_mean, get_text_advice_err, calculate_ar_mean, \
    get_text_advice_ar, get_sex, get_age, find_most_popular_post, top_5_age_sex_category
from strings import text_err, text_ar, text_target_audience


app_layout = html.Div([
    html.Div([

        # Поля ввода контейнер
        html.Div([

            # Поле для ссылки
            html.Div([
                html.P(['Ссылка на сообщество, по которому представлена статистика'],
                       className='link_header',
                       style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px', 'color': '#090447'}),

                html.Div([
                    html.Div(url_start, id='link_display',
                             style={'width': '95%', 'padding': '10px', 'font-size': '18px', 'border-radius': '10px',
                                    'border': '1px solid #ccc', 'color': '#fff'}),
                    html.Button('Копировать ссылку', id='copy_link_button',
                                    style={'font-size': '10px', 'width': 'wrap-content', 'margin-left': '10px', 'border-radius': '10px', 'cursor': 'pointer',
                                           'background-color': '#39344a', 'color': '#fff'}),
                    dcc.Clipboard(target_id="token_display", style={"display": "none"})
                ], style={'margin-bottom': '6px', 'display': 'flex', 'flex-direction': 'row',
                          'justify-content': 'spread-inside'}),
            ], className='row',
                style={'display': 'flex', 'flex-direction': 'column', 'margin-bottom': '10px',
                       'border-radius': '20px'}),

            # Поле для токена (с кнопкой)
            html.Div([
                html.P(['Токен, который вы ввели'],
                       className='token_header',
                       style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px', 'color': '#090447'}),
                html.Div([
                    html.Div('*****', id='token_display',
                             style={'width': '95%', 'padding': '10px', 'font-size': '18px', 'border-radius': '10px',
                                    'border': '1px solid #ccc', 'color': '#fff',
                                    'overflow': 'hidden', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}),
                    html.Button('Копировать токен', id='copy_token_button',
                                style={'font-size': '10px', 'width': 'wrap-content', 'margin-left': '10px', 'border-radius': '10px', 'cursor': 'pointer',
                                       'background-color': '#39344a', 'color': '#fff'}),
                    dcc.Clipboard(target_id="token_display", style={"display": "none"})
                ], style={'margin-bottom': '6px', 'display': 'flex', 'flex-direction': 'row',
                          'justify-content': 'spread-inside'}),
                html.Button('Показать токен', id='show_token_button', n_clicks=0,
                            style={"padding": "10px", "border-radius": "10px", "cursor": "pointer",
                                   'background-color': '#39344a', 'color': '#fff'})
            ], className='row', style={'display': 'flex', 'flex-direction': 'column', 'border-radius': '20px'}),
        ], className='fields_container', style={'grid-column': 'span 6'}),


        # Выбор периода
        html.Div([
            html.P(['Ссылка на сообщество, по которому представлена статистика'],
                       className='link_header',
                       style={'font-style': 'bold', 'font-size': '26px', 'margin-bottom': '10px', 'color': '#090447'}),

            # Радиокнопки
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


@app.callback(
        Output('token_display', 'children'),
        Output('show_token_button', 'children'),
        [Input('show_token_button', 'n_clicks')],
    )
def toggle_token(n_clicks):
    if n_clicks % 2 == 0:
        return '******', 'Показать токен'
    else:
        return access_token, 'Скрыть токен'


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

