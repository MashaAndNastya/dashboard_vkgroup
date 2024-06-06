import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go

text_err = 'Коэффициент охвата (Engagement Rate by Reach) — метрика, которая показывает, сколько людей из тех, что увидели пост, взаимодействовали с ним: комментировали, ставили лайки, делали репосты. Более правильно ERR переводится как коэффициент вовлечённости по охвату.\nКак рассчитать: количество реакций / охват × 100%'
text_arr = 'Annual Recurring Revenue (ARR) — это регулярный ежегодный доход. \nКак расчитать: Количество клиентов * Средний доход с клиента в месяц'

# Данные активности: лайки, комментарии, репосты
data_activity = {
    "Date": pd.to_datetime(["2024-04-01", "2024-04-02", "2024-04-03", "2024-04-04", "2024-04-05"]),
    "Likes": [15, 25, 20, 30, 35],
    "Comments": [5, 10, 15, 10, 5],
    "Reposts": [2, 4, 6, 4, 2]
}
df_activity = pd.DataFrame(data_activity)

# Данные динамики пользователей: просмотры, подписки
data_dinamyc = {
    "Date": pd.to_datetime(["2024-04-01", "2024-04-02", "2024-04-03", "2024-04-04", "2024-04-05"]),
    "Views": [150, 200, 250, 300, 350],
    "Subscriptions": [5, 10, 5, 15, 10]
}
df_dinamyc = pd.DataFrame(data_dinamyc)
text1_err = 'Text 1 ERR'
text1_arr = 'Text 1 ARR'
text1_other = 'Text 1 OTHER'
header1 = 'Header 1'
photo1 = 'Photo 1'
gender1 = [20, 80]
age1 = [10, 20, 50, 20]

text2_err = 'Text 2 ERR'
text2_arr = 'Text 2 ARR'
header2 = 'Header 2'
photo2 = 'Photo 2'
gender2 = [50, 50]
age2 = [60, 10, 20, 10]

# пример графика активности
fig_activity = go.Figure()
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Likes'], mode='lines+markers', name='Likes'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Comments'], mode='lines+markers', name='Comments'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Reposts'], mode='lines+markers', name='Reposts'))
fig_activity.update_layout(title='Activity', xaxis_title='Date', yaxis_title='Count')
fig_activity.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

# пример графика динамики пользователей
fig_dinamyc = go.Figure()
fig_dinamyc.add_trace(go.Scatter(x=df_dinamyc['Date'], y=df_dinamyc['Views'], mode='lines+markers', name='Views'))
fig_dinamyc.add_trace(go.Scatter(x=df_dinamyc['Date'], y=df_dinamyc['Subscriptions'], mode='lines+markers', name='Subscriptions'))
fig_dinamyc.update_layout(title='User Dynamics', xaxis_title='Date', yaxis_title='Count')
fig_dinamyc.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')

# основу dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H4('Trial graph by date'),
            dcc.Dropdown(
                id='day-dropdown',
                options=[
                    {'label': '1', 'value': '1'},
                    {'label': '2', 'value': '2'}
                ],
                value='1',
                style={'color': '#333'},
                className='dcc_compon',
            )
        ], className='row',
            style={'grid-column': 'span 12', 'background-color': '#f9f9f9',
                   'padding': '0px', 'border-radius': '20px'}),

        # график users_activity
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
                   'display': 'flex', 'flex-direction': 'column',  'padding': '20px'}),

        # пост
        html.Div([
            html.P('Самый популярный пост'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='post',
            className='post-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column',  'align-items': 'center', 'padding': '20px'}),

        # график user dynamics
        html.Div([
            dcc.Graph(
                id="users_dinamyc",
                figure=fig_dinamyc,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),

        # ARR сообщества
        html.Div([
            html.P('ARR сообщества'),
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

        # круговая диаграмма М/Ж
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

        # круговая диаграмма возраст
        html.Div([
            dcc.Graph(
                id="age-graph",
                figure=px.pie(
                    values=age1,
                    names=['7-14', '15-29', '30-45', '46-90'],
                    title='Возраст'
                ),
                className='dcc_compon'
            )
        ], id='age',
            style={'grid-column': 'span 3', 'padding': '10px', 'border-radius': '5px', 'background-color': '#39344a'})
    ], className='grid-container', style={'background-color': '#8459822', 'display': 'grid', 'grid-template-columns': 'repeat(12, 1fr)', 'grid-gap': '20px', 'padding': '20px'})
])


# активность график
@app.callback(
    Output('users_activity', 'figure'),
    [Input('day-dropdown', 'value')]
)
def update_activity_graph(selected_option):
    if selected_option == '1':
        updated_fig_activity = go.Figure()
        updated_fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Likes'], mode='lines+markers', name='Likes'))
        updated_fig_activity.add_trace(
            go.Scatter(x=df_activity['Date'], y=df_activity['Comments'], mode='lines+markers', name='Comments'))
        updated_fig_activity.add_trace(
            go.Scatter(x=df_activity['Date'], y=df_activity['Reposts'], mode='lines+markers', name='Reposts'))
        updated_fig_activity.update_layout(
            title='Activity',
            xaxis_title='Date',
            yaxis_title='Count',
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_fig_activity

    elif selected_option=='2':
        updated_fig_activity_2 = go.Figure()
        updated_fig_activity_2.add_trace(
            go.Scatter(x=df_activity['Date'], y=df_activity['Likes'], mode='lines+markers', name='Likes'))
        updated_fig_activity_2.add_trace(
            go.Scatter(x=df_activity['Date'], y=df_activity['Comments'], mode='lines+markers', name='Comments'))
        updated_fig_activity_2.add_trace(
            go.Scatter(x=df_activity['Date'], y=df_activity['Reposts'], mode='lines+markers', name='Reposts'))
        updated_fig_activity_2.update_layout(
            title='Activity',
            xaxis_title='Date',
            yaxis_title='Count',
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_fig_activity_2


# динамика пользователей график
@app.callback(
    Output('users_dinamyc', 'figure'),
    [Input('day-dropdown', 'value')]
)
def update_dinamyc_graph(selected_option):
    if selected_option == '1':
        updated_fig_dinamyc = go.Figure()
        updated_fig_dinamyc.add_trace(
            go.Scatter(x=df_dinamyc['Date'], y=df_dinamyc['Views'], mode='lines+markers', name='Views'))
        updated_fig_dinamyc.add_trace(
            go.Scatter(x=df_dinamyc['Date'], y=df_dinamyc['Subscriptions'], mode='lines+markers', name='Subscriptions'))
        updated_fig_dinamyc.update_layout(
            title='User Dynamics',
            xaxis_title='Date',
            yaxis_title='Count',
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_fig_dinamyc

    elif selected_option == '2':
        updated_fig_dinamyc_2 = go.Figure()
        updated_fig_dinamyc_2.add_trace(
            go.Scatter(x=df_dinamyc['Date'], y=df_dinamyc['Views'], mode='lines+markers', name='Views'))
        updated_fig_dinamyc_2.add_trace(
            go.Scatter(x=df_dinamyc['Date'], y=df_dinamyc['Subscriptions'], mode='lines+markers', name='Subscriptions'))
        updated_fig_dinamyc_2.update_layout(
            title='User Dynamics',
            xaxis_title='Date',
            yaxis_title='Count',
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_fig_dinamyc_2
#ERR
@app.callback(
    Output('ERR', 'children'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':
        updated_text1 = text1_err
        return [
            html.P('ERR сообщества',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(updated_text1,
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
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia',
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   )
        ]
    elif selected_option == '2':
        updated_text2 = text2_err
        return [
            html.P('ERR сообщества',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(updated_text2,
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
                          'font-weight': 'bold'},
                   ),
            html.P(
                'Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia',
                style={'color': '#f9f9f9',
                       'font-size': '12px'}
            )
        ]


#ARR
@app.callback(
    Output('ARR', 'children'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':
        updated_text1 = text1_arr
        return [
            html.P('ARR сообщества',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(updated_text1,
                   style={'color': '#f1986c',
                          'font-size': '34px',
                          'font-weight': 'bold',
                          'mardin-top': '5px',
                          'text-align': 'center'}
                   ),
            html.P(text_arr,
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   ),
            html.P('Советы:',
                   style={'color': '#f9f9f9',
                          'font-size': '20px',
                          'font-weight': 'bold'}
                   ),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia',
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   )
        ]
    elif selected_option == '2':
        updated_text2 = text2_arr
        return [
            html.P('ARR сообщества',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(updated_text2,
            style={'color': '#f1986c',
                   'font-size': '34px',
                   'font-weight': 'bold',
                   'mardin-top': '5px',
                   'text-align': 'center'}
                   ),
            html.P(text_arr,
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   ),
            html.P('Советы:',
                   style={'color': '#f9f9f9',
                          'font-size': '20px',
                          'font-weight': 'bold'},
                   ),
            html.P(
                'Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia',
                style={'color': '#f9f9f9',
                       'font-size': '12px'}
            )
        ]


#М/Ж диаграмма
@app.callback(
    Output('gender-graph', 'figure'),  # Измененный идентификатор для совпадения с id в DIV
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':
        updated_gender1 = px.pie(values=gender1, names=['Male', 'Female'], title='Пол').update_layout(
            legend_orientation='h',
            title_x=0.5,
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_gender1

    elif selected_option == '2':
        updated_gender2 = px.pie(values=gender2, names=['Male', 'Female'], title='Пол').update_layout(
            legend_orientation='h',
            title_x=0.5,
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_gender2


#возраст диаграмма
@app.callback(
    Output('age-graph', 'figure'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':
        updated_age1 = px.pie(values=age1, names=['7-14', '15-29', '30-45', '46-90'], title='Возраст').update_layout(
            legend_orientation='h',
            title_x=0.5,
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_age1

    elif selected_option == '2':
        updated_age2 = px.pie(values=age2, names=['7-14', '15-29', '30-45', '46-90'], title='Возраст').update_layout(
            legend_orientation='h',
            title_x=0.5,
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            font_color='#cbc2b9'
        )
        return updated_age2


#пост
@app.callback(
    Output('post', 'children'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':
        updated_photo1 = photo1
        return [
            html.P('Самый популярный пост',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(updated_photo1,
                   style={'color': '#f1986c',
                          'font-size': '34px',
                          'font-weight': 'bold',
                          'mardin-top': '5px',
                          'text-align': 'center'}
                   ),
            html.P('Ссылка 1',
                   style={'color': '#f9f9f9',
                          'font-size': '12px'}
                   )
        ]
    elif selected_option == '2':
        updated_photo2 = photo2
        return [
            html.P('Самый популярный пост',
                    style={'color': '#f9f9f9',
                           'font-size': '24px',
                           'font-weight': 'bold',
                           'mardin-bottom': '5px',
                           'text-align': 'center'}
                   ),
            html.P(updated_photo2,
            style={'color': '#f1986c',
                   'font-size': '34px',
                   'font-weight': 'bold',
                   'mardin-top': '5px',
                   'text-align': 'center'}
                   ),
            html.P(
                'Ссылка 2',
                style={'color': '#f9f9f9',
                       'font-size': '12px'}
            )
        ]


if __name__ == '__main__':
    app.run_server(debug=True)
