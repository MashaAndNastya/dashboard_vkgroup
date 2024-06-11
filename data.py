import pandas as pd
import requests
import time
from datetime import datetime, timezone, date, timedelta


#Изначальные переменные, потом будут передаваться через поле для ввода
url_start = 'https://vk.com/dimdimychmusic'
url = url_start.split('/')
access_token = "vk1.a.zPEtzBOVfFVEnCAaT2cMvW6CYvsFyOFiB8NFFU9GEz-sWujzUYZuA00WoHRpykSBtNni2EkFM4s4xLB_4_CcWk5SjN-pyh0xoe-pH4OO0CxWWzY1fXxsAzYq0dCXwHimF3p_is6GIyH_wvL0yCGd3SFKeBncr_NOpuodwPr7Hr6Zi9YrG8AQqVtp3Jo-jzA_cFS-1WKcAYnA06vt18QxZg"
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




