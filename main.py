# Делает резервное копирование фотографий профиля ВК на яндекс диск.
# Для работы программы необходимо создать объект класса VK_backup, в качестве атрибутов передать id
# пользователя ВК и OAuth-token API яндекс диска. Вызвать метод backup для созданного объекта класса.
# Результат - скопированные на яндекс диск фото и созданный в директории с файлом программы JSON файл
# с информацией по фото.
import requests
from pprint import pprint
import json
from logs import logs

logs()


class VK_backup:
    token_vk = ('yor token')
    base_url_vk = 'https://api.vk.com/method'
    base_url_ya = 'https://cloud-api.yandex.net'

    def __init__(self, vk_id, ya_token):
        self.vk_id = vk_id
        self.ya_token = ya_token
        self.headers_ya = {'Authorization': self.ya_token}

    def create_dir(self):
        """
        Создаёт папку для хранения фото на яндекс диске
        :return: str
        """
        url = '/v1/disk/resources'
        params = {'path': 'profile_photos'}
        requests.put(f'{self.base_url_ya}{url}', params=params, headers=self.headers_ya)
        return params['path']

    def get_photos_info(self):
        """
        Возвращает полную информацию по фотографиям в JSON формате
        :return: JSON
        """
        params = self._get_common_params_VK()
        params.update({'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(f'{self.base_url_vk}/photos.get', params=params).json()
        return response

    def get_photos_url(self):
        """
        Возвращает список url фото для скачивания
        :return: list
        """
        names_urls = {}
        for item in self.get_photos_info()['response']['items']:
            if item['likes']['count'] not in names_urls:
                names_urls[item['likes']['count']] = item['sizes'][-1]['url']
            else:
                names_urls[f'{item['likes']['count']}, {item['date']}'] = item['sizes'][-1]['url']
        return names_urls

    def save_photos_info(self):
        """
        Сохраняет информацию о скачиваемых фото в JSON файл
        :return: JSON
        """

    def download_photos(self):
        """
        Скачивает фото по url в специальную директорию
        :return: None
        """
        for name, url in self.get_photos_url().items():
            response = requests.get(url)
            with open(f'vk_photos/{name}.jpg', "wb") as f:
                f.write(response.content)

    def _get_common_params_VK(self):
        """
        Хранит неизменные параметры для API ВК
        :return: dict
        """
        params = {'access_token': self.token_vk, 'v': '5.131'}
        return params


if __name__ == '__main__':
    token_ya = 'your token'
    id_ = 'your id'
    backup = VK_backup(id_, token_ya)
    # print(backup.create_dir())
    # pprint(backup.get_photos_url())
    # backup.download_photos()
