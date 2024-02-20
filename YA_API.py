import requests
import json
import configparser
from logger import logs
from VK_API import VkApi

logs()
config = configparser.ConfigParser()
config.read("tokens.ini")

id_ = input('Введите Ваш ID или screen_name без пробелов')
count_ = input('Введите количество копируемых фото (по умолчанию 5)')
if count_ == "":
    count_ = 5
count_ = int(count_)


class YaApi:
    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': self.token}
        self.user_vk = user_vk

    def create_dir(self, path):
        """
        Создаёт папку для хранения фото на яндекс диске
        :param path: str
        :return: None
        """
        url = '/v1/disk/resources'
        params = {'path': path}
        response = requests.put(f'{self.base_url}{url}', params=params, headers=self.headers)
        if response.status_code != 201:
            raise Exception(f'wrong response, status code = {response.status_code}')

    def backup(self, count, path='vk_profile_photos', file_name='photo_info.json'):
        """
        Сохраняет загруженные фото на яндекс диске и создаёт JSON файл с инфо по фото
        :param count: int
        :param path: str
        :param file_name: str
        :return: None
        """
        loaded = 0
        data_for_json = []
        self.create_dir(path)
        for name, url_size in self.user_vk.get_valid_photos_info().items():
            if loaded < count:
                upload_url = f'{self.base_url}/v1/disk/resources/upload'
                params = {'path': f'{path}/{name}', 'url': url_size[0]}
                response = requests.post(upload_url, params=params, headers=self.headers)
                if response.status_code != 202:
                    raise Exception(f'wrong response, status code = {response.status_code}')
                loaded += 1
                data_for_json.append({'file_name': name, 'size': url_size[1]})
            else:
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(data_for_json, f, indent=4)
                break
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data_for_json, f, indent=4)


user_vk = VkApi(id_)
user_ya = YaApi(config['TOKENS']['ya_token'])
user_ya.backup(count_)
