import pandas as pd
import requests
import time
from datetime import datetime
#Изначальные переменные, потом будут передаваться через поле для ввода
url_start = 'https://vk.com/dimdimychmusic'
url = url_start.split('/')
access_token = "vk1.a.zPEtzBOVfFVEnCAaT2cMvW6CYvsFyOFiB8NFFU9GEz-sWujzUYZuA00WoHRpykSBtNni2EkFM4s4xLB_4_CcWk5SjN-pyh0xoe-pH4OO0CxWWzY1fXxsAzYq0dCXwHimF3p_is6GIyH_wvL0yCGd3SFKeBncr_NOpuodwPr7Hr6Zi9YrG8AQqVtp3Jo-jzA_cFS-1WKcAYnA06vt18QxZg"
domain = url[-1]
#константные переменные
version = 5.199
count = 100
offset = 0
#получаем id группы через запрос
response = requests.get('https://api.vk.com/method/utils.resolveScreenName',
                        params={'access_token': access_token,
                                'screen_name': domain,
                                'v': version})
id_group = response.json()['response']['object_id']

#стартовое и конечное значение в формате unix-времени, тк вводится в fetch_stats только UNIX время
start_time = '1709286555'
end_time = '1713174555'
#перевод во временной промежуток(список) для построения графика
date_range = pd.date_range(start=pd.to_datetime(start_time, unit='s').date(), end=pd.to_datetime(end_time, unit='s').date())





def fetch_vk_data(access_token, version, count, offset):
    data_dict = {
        'ID': [],
        'Text': [],
        'Likes': [],
        'Comments': [],
        'Views': [],
        'Reposts': [],
        'URL': [],
        'Date': [],
        'Date_UNIX': []
    }



    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': access_token,
                                    'v': version,
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
        data_dict['Date'].extend([datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d') for item in data])
        data_dict['Date_UNIX'].extend([item['date'] for item in data])
        time.sleep(0.01)

    df_posts = pd.DataFrame(data_dict)
    print(df_posts.columns)
    return df_posts


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
    # Initialize empty lists to store the extracted data
    likes, copies, hidden, comment, subscribed, unsubscribed, reach1, reach_subscribers, reach_unique_user = [], [], [], [], [], [], [], [], []
    sex_f, sex_m = [], []
    age_data = {}
    age_sex_data = {}

    for item in response_data:
        activity = item.get("activity", {})  # Handle empty "activity" case
        reach = item.get("reach", {})

        # Extracting activity data
        likes.append(activity.get("likes", 0))
        copies.append(activity.get("copies", 0))
        hidden.append(activity.get("hidden", 0))
        comment.append(activity.get("comment", 0))
        subscribed.append(activity.get("subscribed", 0))
        unsubscribed.append(activity.get("unsubscribed", 0))
        reach1.append(reach.get("reach", 0))
        reach_subscribers.append(reach.get("reach_subscribers", 0))
        reach_unique_user. append(reach1[-1]-reach_subscribers[-1])
        # Extracting sex data
        for sex in reach.get("sex", []):
            if sex["value"] == "f":
                sex_f.append(sex["count"])
            elif sex["value"] == "m":
                sex_m.append(sex["count"])

        # Extracting age data
        for age_group in reach.get("age", []):
            age_data[age_group["value"]] = age_group["count"]

        # Extracting sex-age data
        for sex_age in reach.get("sex_age", []):
            age_sex_data[sex_age["value"]] = sex_age["count"]

    sex_df = pd.DataFrame({"f": sex_f, "m": sex_m})
    age_df = pd.DataFrame(list(age_data.items()), columns=["age_group", "count"])
    age_sex_df = pd.DataFrame(list(age_sex_data.items()), columns=["sex_age", "count"])
    return likes, copies, hidden, comment, subscribed, unsubscribed, reach1, reach_subscribers, reach_unique_user, sex_df, age_df, age_sex_df

#Вызов функции, запись  в переменные и постобработка данных
likes, copies, hidden, comment, subscribed, unsubscribed, reach, reach_subscribers, reach_unique_user, sex_df, age_df, age_sex_df = fetch_vk_stats(start_time, end_time, access_token, id_group)
count_female = sum(sex_df['f'])
count_male = sum(sex_df['m'])
age_12_21 = age_df[(age_df['age_group'] == '12-18')]['count'].values[0]+age_df[(age_df['age_group'] == '18-21')]['count'].values[0]
age_21_27 = age_df[(age_df['age_group'] == '21-24')]['count'].values[0]+age_df[(age_df['age_group'] == '24-27')]['count'].values[0]
age_27_30 = age_df[(age_df['age_group'] == '27-30')]['count'].values[0]+age_df[(age_df['age_group'] == '30-35')]['count'].values[0]
age_35_45 = age_df[(age_df['age_group'] == '35-45')]['count'].values[0]
age_45_100 = age_df[(age_df['age_group'] == '45-100')]['count'].values[0]

#расчёт ARR и ERR
err_mean = ((sum(likes)+sum(copies)+sum(comment))/sum(reach))*100
if err_mean<=1:
    text_advice_err="По общим стандартам ваш показатель ERR низкий."
elif err_mean>1 and err_mean<=3.5:
    text_advice_err = "По общим стандартам ваш показатель ERR средний, сложно сделать вывод об эффективности вашего сообщества."
else:
    text_advice_err = "Поздравляем! По общим стандартам ваш показатель ERR высокий."

#вычисление самого популярного поста
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
    filtered_df['Popularity'] = (
                df['Likes'] * like_weight + df['Views'] * view_weight + df['Comments'] * comment_weight)

    # Определение самого популярного поста
    most_popular_post = filtered_df.loc[filtered_df['Popularity'].idxmax()]

    return most_popular_post


most_popular_post = find_most_popular_post(df, start_time, end_time, like_weight=0.5, view_weight=0.3, comment_weight=0.2)
print(date_range)
print(most_popular_post)
