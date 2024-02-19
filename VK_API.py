import requests
import configparser
from logger import logs

logs()

config = configparser.ConfigParser()
config.read("tokens.ini")


class VkApi:
    base_url = 'https://api.vk.com/method'
    params = {'access_token': config['TOKENS']['vk_token'], 'v': '5.131'}

    def __init__(self, vk_id):
        self.vk_id = vk_id

    def get_photos_info(self):
        """
        Возвращает полную информацию по фото в JSON формате
        :return: JSON
        """
        if not self.vk_id.isdigit():
            self.vk_id = self.get_id_from_screen_name()
        self.params.update({'owner_id': self.vk_id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(f'{self.base_url}/photos.get', params=self.params)
        if response.status_code != 200:
            raise Exception(f'wrong response, status code = {response.status_code}')
        response_json = response.json()
        if list(response_json.keys())[0] == 'error':
            raise Exception([response_json['error']['error_msg']])
        return response_json

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

    def get_id_from_screen_name(self):
        """
        Возвращает цифровой id пользователя по screen_name
        :return: int
        """
        self.params.update({'screen_name': self.vk_id})
        response = requests.get(f'{self.base_url}/utils.resolveScreenName', params=self.params)
        if response.status_code != 200:
            raise Exception(f'wrong response, status code = {response.status_code}')
        response_json = response.json()
        return response_json['response']['object_id']
