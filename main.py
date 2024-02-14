# Делает резервное копирование фотографий профиля ВК на яндекс диск.
# Для работы программы необходимо создать объект класса VK_backup, в качестве атрибутов передать id
# пользователя ВК и OAuth-token API яндекс диска. Для созданного объекта класса вызвать метод backup
# с указанием количества сохраняемых фото (по умолчанию 5).
# Результат - сохранённые на яндекс диск фото и созданный в директории с файлом программы JSON файл
# с информацией по фото.


import requests
import json
from logger import logs

logs()


class VK_backup:
    base_url_vk = 'https://api.vk.com/method'
    base_url_ya = 'https://cloud-api.yandex.net'
    params_vk = {'access_token': 'Your token', 'v': '5.131'}

    def __init__(self, vk_id, ya_token):
        self.vk_id = vk_id
        self.ya_token = ya_token
        self.headers_ya = {'Authorization': self.ya_token}

    def get_photos_info(self):
        """
        Возвращает полную информацию по фото в JSON формате
        :return: JSON
        """
        self.params_vk.update({'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(f'{self.base_url_vk}/photos.get', params=self.params_vk)
        if response.status_code != 200:
            raise Exception(f'wrong response, status code = {response.status_code}')
        response_JSON = response.json()
        if list(response_JSON.keys())[0] == 'error':
            raise Exception([response_JSON['error']['error_msg']])
        return response_JSON

    def get_valid_photos_info(self):
        """
        Возвращает словарь с именами, url и размерами фото для скачивания и записи в JSON
        :return: dict
        """
        valid_info = {}
        for item in self.get_photos_info()['response']['items']:
            if f'{item['likes']['count']}' not in valid_info:
                valid_info[f'{item['likes']['count']}'] = item['sizes'][-1]['url'], item['sizes'][-1]['type']
            else:
                valid_info[f'{item['likes']['count']}, {item['date']}'] = (item['sizes'][-1]['url'],
                                                                           item['sizes'][-1]['type'])
        return valid_info

    def create_dir(self, path):
        """
        Создаёт папку для хранения фото на яндекс диске
        :param path: str
        :return: None
        """
        url = '/v1/disk/resources'
        params = {'path': path}
        response = requests.put(f'{self.base_url_ya}{url}', params=params, headers=self.headers_ya)
        if response.status_code != 201:
            raise Exception(f'wrong response, status code = {response.status_code}')

    def get_upload_url(self, path):
        """
        Возвращает url для загрузки фото на яндекс диск
        :param path: str
        :return: str
        """
        url_for_url = f'{self.base_url_ya}/v1/disk/resources/upload'
        params = {'path': path}
        headers = self.headers_ya
        response = requests.get(url_for_url, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f'wrong response, status code = {response.status_code}')
        response_JSON = response.json()
        return response_JSON['href']

    def backup(self, count=5, path='vk_profile_photos'):
        """
        Сохраняет загруженные фото на яндекс диске и создаёт JSON файл с инфо по фото
        :param count: int
        :param path: str
        :return: None
        """
        loaded = 0
        data_for_JSON = []
        self.create_dir(path)
        for name, url_size in self.get_valid_photos_info().items():
            if loaded < count:
                response = requests.get(url_size[0])
                with open(f'{name}.jpg', "wb") as f:
                    f.write(response.content)
                upload_url = self.get_upload_url(f'{path}/{name}.jpg')
                with open(f'{name}.jpg', 'rb') as f:
                    requests.put(upload_url, files={"file": f})
                loaded += 1
                data_for_JSON.append({'file_name': name, 'size': url_size[1]})
            else:
                with open('photo_info.json', 'w', encoding='utf-8') as f:
                    json.dump(data_for_JSON, f, indent=4)
                break
        with open('photo_info.json', 'w', encoding='utf-8') as f:
            json.dump(data_for_JSON, f, indent=4)


if __name__ == '__main__':
    token_ya = 'Your token'
    id_ = 'Your id'
    backup = VK_backup(id_, token_ya)
    backup.backup()
