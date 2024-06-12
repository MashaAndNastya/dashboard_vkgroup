from datetime import datetime, timezone
import time
import pandas as pd
import requests
from dialog_window import access_token, domain, url_start


# Получаем id группы через запрос
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
                # # Получение аватарки группы
                # main_photo_response = requests.get('https://api.vk.com/method/photos.get',
                #                                    params={
                #                                        'access_token': access_token,
                #                                        'owner_id': '-' + str(id_group),
                #                                        'album_id': 'profile',
                #                                        'rev': 1,
                #                                        'count': 1,
                #                                        'v': version
                #                                    })
                # main_photo_data = main_photo_response.json()
                # if 'response' in main_photo_data and 'items' in main_photo_data['response'] and \
                #         main_photo_data['response']['items']:
                #     main_photo_url = main_photo_data['response']['items'][0]['sizes'][-1]['url']
                #     data_dict['Photo'].append(main_photo_url)
                # else:
                #     data_dict['Photo'].append("No photo")

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
