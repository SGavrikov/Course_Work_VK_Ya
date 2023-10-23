import json
import requests
from datetime import datetime
import pyprind
import sys
import time


class VK:
    API_BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, user_id, token):
        self.token = token
        self.user_id = user_id

    def get_profile_photos(self):
        params = {
        'access_token': self.token,
        'v': '5.131',
        'owner_id': self.user_id,
        'album_id': 'profile',
        'extended': '1',
        'count': '1000'
            }
        response = requests.get(self.API_BASE_URL + 'photos.get', params=params)
        if 'error' in response.json().keys():
            print('Ошибка авторизации, проверьте токен')
        else:
            print(f"В альбоме аккаунта VK ID {self.user_id} содержится {response.json()['response']['count']} фото")
            return response.json()['response']['items']

    def create_photo_base(self):
        photo_base = self.get_profile_photos()

        # создание cписка словарей, остортированного по размеру фото (в байтах)
        # - у фото до 2012 года отсуствуют парамеры высоты и ширины
        # размер фото взят реальный (по ссылке), можно сделать сортировкой по типу размера, но это не точно
        photos_list = []
        print('Сортировка всех фотографий из VK по размеру')
        bar = pyprind.ProgBar(len(photo_base), stream=sys.stdout)  # создание прогресс-бара создания базы фотографий
        for photo in photo_base:
            response = requests.head(photo['sizes'][-1]['url'])  # запрос заголовков для определения размера фото
            photos_list.append([int(response.headers['Content-Length']),
                                {'likes': photo['likes']['count'], 'url': photo['sizes'][-1]['url'],
                                'size': photo['sizes'][-1]['type'], 'date': photo['date']}])
            time.sleep(0.1)
            bar.update()
        photos_list.sort(key=lambda x: int(x[0]), reverse=True)
        return photos_list

    def yandex_load(self, token, folder_name='Photos from VK'):
        headers_ya = {'Authorization': f'OAuth {token}'}
        # создание папки на ЯД (c ID пользователя)
        folder_name += f' ID {self.user_id}'
        response = requests.put(f'https://cloud-api.yandex.net/v1/disk/resources?path={folder_name}',
                                headers=headers_ya)
        if 'error' in response.json().keys():
            print(f'Папка {folder_name} уже существует на ЯД')
        else:
            print(f'Папка {folder_name} на ЯД создана')

        # создание базы фото с ВК
        photos_list = self.create_photo_base()
        photo_count = int(input('Cколько фото вы хотите загрузить на ЯД (по умолчанию - 5) ') or "5")

        # создание множества равных количеств лайков
        set_of_likes = set()
        set_of_equal_likes = set()
        for photo in photos_list:
            if photo[1]['likes'] in set_of_likes:
                set_of_equal_likes.add(photo[1]['likes'])
            set_of_likes.add(photo[1]['likes'])

        # проверка наличия нужного количества фото в ВК
        if len(photos_list) < photo_count:
            photo_count = len(photos_list)
        print('Загрузка фото на ЯД')
        result = []  # список для записи отчетного json
        bar = pyprind.ProgBar(photo_count, stream=sys.stdout)  # создание прогресс-бара загрузки файлов на ЯД
        for elem in range(photo_count):
            if photos_list[elem][1]['likes'] in set_of_equal_likes:
                date = str(datetime.fromtimestamp(photos_list[elem][1]['date'])).replace(':', '_')
                file_name = f"{photos_list[elem][1]['likes']}-{date}.jpg"
            else:
                file_name = f"{photos_list[elem][1]['likes']}.jpg"

            result.append({"file_name": file_name, "size": photos_list[elem][1]['size']})
            response_vk_load = requests.get(photos_list[elem][1]['url'])
            params = {'path': f"{folder_name}/{file_name}", 'overwrite': 'true'}
            response_ya_upload = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                              params=params, headers=headers_ya)
            url_for_upload = response_ya_upload.json()['href']
            requests.put(url_for_upload, files={"file": response_vk_load.content})
            time.sleep(0.1)
            bar.update()
        with open('photos.json', 'w') as outfile:
            json.dump(result, outfile)
        print(f'В папку "{folder_name}" на ЯД загружено {photo_count} фото максимального размера')


if __name__ == '__main__':
    # vk_id = input('Введите VK ID \n ')
    # vk_token = input('Введите VK token \n ')
    # ya_token = input('Введите Yandex token \n ')
    # vk_client = VK(vk_id, vk_token)
    # vk_client.yandex_load(ya_token)
