# Делает резервное копирование фотографий профиля ВК на яндекс диск.
# Для работы программы необходимо создать объект класса VK_backup, в качестве атрибутов передать id
# пользователя ВК и OAuth-token API яндекс диска. Для созданного объекта класса вызвать метод backup
# с указанием количества сохраняемых фото (по умолчанию 5).
# Результат - сохранённые на яндекс диск фото и созданный в директории с файлом программы JSON файл
# с информацией по фото.
# ОБРАБОТАТЬ ИСКЛЮЧЕНИЯ, ПЕРЕДЕЛАТЬ def save_photos_info(self)
import requests
import json
from logs import logs

logs()


class VK_backup:
    base_url_vk = 'https://api.vk.com/method'
    base_url_ya = 'https://cloud-api.yandex.net'
    params_vk = {'access_token': 'your token', 'v': '5.131'}

    def __init__(self, vk_id, ya_token):
        self.vk_id = vk_id
        self.ya_token = ya_token
        self.headers_ya = {'Authorization': self.ya_token}

    def create_dir(self, path):
        """
        Создаёт папку для хранения фото на яндекс диске
        :param path: str
        :return: None
        """
        url = '/v1/disk/resources'
        params = {'path': path}
        requests.put(f'{self.base_url_ya}{url}', params=params, headers=self.headers_ya)

    def get_photos_info(self):
        """
        Возвращает полную информацию по фотографиям в JSON формате
        :return: JSON
        """
        self.params_vk.update({'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(f'{self.base_url_vk}/photos.get', params=self.params_vk).json()
        return response

    def get_valid_photos_info(self):
        """
        Возвращает список имён и url фото для скачивания и инфо для записи в JSON
        :return: dict, list[dict]
        """
        names_urls = {}
        info_for_JSON = []
        for item in self.get_photos_info()['response']['items']:
            if item['likes']['count'] not in names_urls:
                names_urls[item['likes']['count']] = item['sizes'][-1]['url']
                # info_for_JSON.append({'file_name': f'{item['likes']['count']}.jpg',
                #                       'size': item['sizes'][-1]['type']})
            else:
                names_urls[f'{item['likes']['count']}, {item['date']}'] = item['sizes'][-1]['url']
                # info_for_JSON.append({'file_name': f'{item['likes']['count']}, {item['date']}.jpg',
                #                       'size': item['sizes'][-1]['type']})
        return names_urls, info_for_JSON

    def save_photos_info(self):
        """
        Сохраняет информацию о скачиваемых фото в JSON файл
        :return: None
        """
        with open('photo_info.json', 'w', encoding='utf-8') as f:
            json.dump(self.get_valid_photos_info()[1], f, indent=4)

    def save_photos(self, count=5, path='vk_profile_photos'):
        """
        Сохраняет загруженные фото на яндекс диске
        :param count: int
        :param path: str
        :return: None
        """
        self.create_dir(path)
        loaded = 0
        for name, url in self.get_valid_photos_info()[0].items():
            if loaded < count:
                response = requests.get(url)
                with open(f'{name}.jpg', "wb") as f:
                    f.write(response.content)
                upload_url = self.get_upload_url(f'{path}/{name}.jpg')
                with open(f'{name}.jpg', 'rb') as f:
                    requests.put(upload_url, files={"file": f})
                loaded += 1
            else:
                break

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
            raise Exception(f'response ERROR, status code = {response.status_code}')
        response_JSON = response.json()
        return response_JSON['href']

    def backup(self, count=5):
        """
        Сохраняет фото на яндекс диске и создаёт JSON файл с инфо по фото
        :param count: int
        :return: None
        """
        self.save_photos(count)
        self.save_photos_info()


if __name__ == '__main__':
    token_ya = 'your token'
    id_ = 'your id'
    backup = VK_backup(id_, token_ya)
    backup.backup()
