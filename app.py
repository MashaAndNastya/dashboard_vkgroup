import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


text_err = 'Коэффициент охвата (Engagement Rate by Reach) — метрика, которая показывает, сколько людей из тех, что увидели пост, взаимодействовали с ним: комментировали, ставили лайки, делали репосты. Более правильно ERR переводится как коэффициент вовлечённости по охвату.\nКак рассчитать: количество реакций / охват × 100%'
text_arr = 'Annual Recurring Revenue (ARR) — это регулярный ежегодный доход. \nКак расчитать: Количество клиентов * Средний доход с клиента в месяц'

# данные 1
data1 = {
    "Date": pd.to_datetime(["2024-04-01", "2024-04-02", "2024-04-03", "2024-04-04", "2024-04-05"]),
    "Value": [15, 25, 20, 30, 35]
}
df1 = pd.DataFrame(data1)

fig1 = px.line(df1, x='Date', y='Value', title='Graph 1')

text1 = 'Text 1'
header1 = 'Header 1'

photo1 = 'Photo 1'

gender1 = [20, 80]
age1 = [10, 20, 50, 20]

# данные 2
data2 = {
    "Date": pd.to_datetime(["2024-04-01", "2024-04-02", "2024-04-03", "2024-04-04", "2024-04-05"]),
    "Value": [15, 13, 10, 5, 2]
}
df2 = pd.DataFrame(data2)

fig2 = px.line(df2, x='Date', y='Value', title='Graph 2')

text2 = 'Text 2'
header2 = 'Header 2'

photo2 = 'Photo 2'

gender2 = [50, 50]
age2 = [60, 10, 20, 10]

#пишем основу
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

        #график users_activity
        html.Div([
            dcc.Graph(
                id="users_activity",
                figure=fig1,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),

        #ERR сообщества
        html.Div([
            html.P('ERR сообщества'),
            html.P(text1),
            html.P(text_err),
            html.P('Советы:'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='ERR',
            className='text-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column',  'padding': '20px'}),


        #пост
        html.Div([
            html.P('Самый популярный пост'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='post',
            className='post-container',
            style={'background-color': '#39344a', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column',  'align-items': 'center', 'padding': '20px'}),


        #график user dinamyc
        html.Div([
            dcc.Graph(
                id="users_dinamyc",
                figure=fig1,
                className='dcc_compon'
            )
        ], style={'grid-column': 'span 6', 'border-radius': '5px', 'background-color': '#39344a', 'padding': '10px'}),


        #ARR сообщества
        html.Div([
            html.P('ARR сообщества'),
            html.P(text1),
            html.P(text_arr),
            html.P('Советы:'),
            html.P('Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia Mama mia mama mama mia mama mia')
        ], id='ARR',
            className='text-container',
            style={'background-color': '#39344a', 'padding': '20px', 'border-radius': '5px', 'grid-column': 'span 3',
                   'display': 'flex', 'flex-direction': 'column'}),

        #Какие-то еще метрики
        html.Div([
            html.H6("Random Text Container 1", style={'color': '#FFFFFF', 'fontWeight': 'bold'}),
            html.P(text1)
        ], className='text-container',
            style={'background-color': '#333333', 'padding': '20px', 'border-radius': '5px', 'grid-column': 'span 3'}),

        #круговая диаграмма М/Ж
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

        #круговая диаграмма возраст
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


#активность график
@app.callback(
    Output('users_activity', 'figure'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':

        updated_fig_users_activity1 = px.line(df1, x='Date', y='Value', title='Graph 1').update_traces(
            line=dict(color='#f1986c'),
            marker=dict(color='#f1986c'),
        ).update_layout(
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            xaxis={
                'title': 'Время',
                'color': '#cbc2b9'
            },
            yaxis={
                'title': 'Число пользователей',
                'color': '#cbc2b9'
            },
            title={
                'text': 'Активность',
                'font': {'color': '#cbc2b9'}  # Цвет шрифта заголовка
            }
        )
        return updated_fig_users_activity1

    elif selected_option == '2':

        updated_fig_users_activity2 = px.line(df2, x='Date', y='Value', title='Graph 2').update_traces(
            line=dict(color='#f1986c'),
            marker=dict(color='#f1986c'),
        ).update_layout(
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            xaxis={
                'title': 'Время',
                'color': '#cbc2b9'
            },
            yaxis={
                'title': 'Число пользователей',
                'color': '#cbc2b9'
            },
            title={
                'text': 'Активность',
                'font': {'color': '#cbc2b9'}  # Цвет шрифта заголовка
            }
        )

        return updated_fig_users_activity2


#пользователи динамика график
@app.callback(
    Output('users_dinamyc', 'figure'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':

        updated_fig_users_dinamyc1 = px.line(df1, x='Date', y='Value', title='Graph 1').update_traces(
            line=dict(color='#f1986c'),
            marker=dict(color='#f1986c'),
        ).update_layout(
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            xaxis={
                'title': 'Время',
                'color': '#cbc2b9'
            },
            yaxis={
                'title': 'Число пользователей',
                'color': '#cbc2b9'
            },
            title={
                'text': 'Динамика пользователей',
                'font': {'color': '#cbc2b9'}
            }
        )
        return updated_fig_users_dinamyc1

    elif selected_option == '2':

        updated_fig_users_dinamyc2 = px.line(df2, x='Date', y='Value', title='Graph 2').update_traces(
            line=dict(color='#f1986c'),
            marker=dict(color='#f1986c'),
        ).update_layout(
            plot_bgcolor='#39344a',
            paper_bgcolor='#39344a',
            xaxis={
                'title': 'Время',
                'color': '#cbc2b9'
            },
            yaxis={
                'title': 'Число пользователей',
                'color': '#cbc2b9'
            },
            title={
                'text': 'Динамика пользователей',
                'font': {'color': '#cbc2b9'}
            }
        )

        return updated_fig_users_dinamyc2


#ERR
@app.callback(
    Output('ERR', 'children'),
    [Input('day-dropdown', 'value')]
)
def update_graph(selected_option):
    if selected_option == '1':
        updated_text1 = text1
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
        updated_text2 = text2
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
        updated_text1 = text1
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
        updated_text2 = text2
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
