import yadisk
import os
import requests
import json
import datetime
import time
from tqdm import tqdm
from progress.bar import IncrementalBar
from urllib.parse import urlencode
from http.client import responses
from collections import Counter
from pprint import pprint

class VKAPIClient:
    url_vk = 'https://api.vk.com/method/'
    def __init__(self,token,user_id,count_foto):
        self.token = token
        self.user_id = user_id
        self.count_foto = count_foto
    def users_info(self):
        url_vk_metod = self.url_vk+'users.get'
        params = {'user_ids': self.user_id,
                  'access_token': self.token,
                  'v': 5.199}
        response = requests.get(url_vk_metod, params=params)
        return response.json()
    def get_foto_profile(self):
        url_vk_metod = self.url_vk + 'photos.get'
        params = {'access_token': self.token,
                  'user_ids': self.user_id,
                  'album_id': 'profile',
                  'extended': 'likes',
                  'count': self.count_foto,
                  'v': 5.199}
        response = requests.get(url_vk_metod, params=params)
        return response.json()

class YandexAPIClient:
    url_ya = 'https://cloud-api.yandex.net/v1/disk/resources'
    def __init__(self, yandex_token):
        self.token = yandex_token
    def yandex_info(self,yandex_folder_name):
        headers = {'Authorization': self.token}
        params = {'path': yandex_folder_name}
        response = requests.get(self.url_ya, params=params, headers=headers)
        return response.status_code
    def yandex_delete_folder(self,yandex_folder_name):
        headers = {'Authorization': self.token}
        params = {'path': yandex_folder_name}
        response = requests.delete(self.url_ya, params=params, headers=headers)
        return response.json()
    def yandex_creet_folder(self,yandex_folder_name):
        headers = {'Authorization': self.token}
        params = {'path': yandex_folder_name}
        response = requests.put(self.url_ya, params=params, headers=headers)
        return response.json()
    def yandex_save_foto(self,yandex_folder_name, spisok_foto):
        url_ya_metod = self.url_ya + '/upload'
        headers = {'Authorization': self.token}
        j=0
        while j < len(spisok_foto):
            params = {'url': spisok_foto[j][1],
                      'path': f'{yandex_folder_name}/{spisok_foto[j][0]}.jpg'}
            response = requests.post(url_ya_metod, headers=headers, params=params )
            j+=1
        return response.json()
    def yandex_save_file(self,yandex_folder_name, file_name):
        url_ya_metod = self.url_ya + '/upload'
        headers = {'Authorization': self.token}
        params = {'url': file_name ,
                  'path': yandex_folder_name}
        response = requests.post(url_ya_metod, headers=headers, params=params )
        return response.json()
    def upload_file(self, loadfile, savefile, replace=False):
        """Загрузка файла.
            savefile: Путь к файлу на ЯДиске
            loadfile: Путь к загружаемому файлу
            replace: true or false Замена файла на Диске"""
        url_ya_metod = self.url_ya + '/upload'
        params = {'path': savefile,
                  'overwrite': replace}
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        res = (requests.get(url_ya_metod, headers=headers, params=params)).json()
        with open(loadfile, 'rb') as f:
            requests.put(res['href'], files={'file': f})

"<----------Обьявления обязательных данных"

#Входные данные: id пользователя, Токен VK, Токен Яндекс диска, Имя папки (куда будут сохраняться фото на Яндекс Диске),
vk_user_id = ''
vk_token = ''
yandex_token = ''
count_foto = 5  #необходимое колличество фотографий которое надо скачать

"<----------Конец обьявления обязательных данных"

#Задаются имена папки на Яндекс Диске и файлов json и txt
yandex_folder_name = '0_Belyaev_A_A_VK_foto_profile'
file_name_json = '0_Spisok_Belyaev_A_A.json'
#Задается расположение файла json на Яндекс диске
savefile = f'{yandex_folder_name}/{file_name_json}'
#Задается расположение файла json на ПК
loadfile = file_name_json

#Создаем обьект VK
vk_client = VKAPIClient(vk_token,vk_user_id,count_foto)
#1. Берем словарь с информаций о фото аватарок'
dict_foto = vk_client.get_foto_profile()   #Берем словарь с информаций о фото аватарок

index = 0
index_2 = 0
index_like = 0
spisok_foto = []
spisok_true = []
spisok_like = []

#2. Собираем у каждой фотографии кол-во лайков в список - "spisok_like"'
while index_like < count_foto:
    p=dict_foto['response']['items'][index_like]['likes']['count']
    spisok_like.append(dict_foto['response']['items'][index_like]['likes']['count'])
    index_like += 1

#3. Формируются два списка:
#   "spisok_foto" - имя файла и его URL
#   "spisok_true" - имя файла и его индекс (vk) максимального размера
while index < count_foto:
    for variable in dict_foto['response']['items'][index]['sizes']:
        height_foto_max = int(dict_foto['response']['items'][index ]['orig_photo']['height'])
        width_foto_max = int(dict_foto['response']['items'][index]['orig_photo']['width'])
        if int(variable['height']) >= height_foto_max and int(variable['width']) >= width_foto_max:
            height_foto_max = variable['height']
            foto_url = variable['url']
            foto_size = variable['type']
        index_2 += 1
    index_2 = 0
    foto_like = dict_foto['response']['items'][index]['likes']['count']
    foto_id = dict_foto['response']['items'][index]['id']

    Counter_spisok_like=Counter(spisok_like)

    d=Counter_spisok_like[foto_like]
    if foto_like in Counter_spisok_like and Counter_spisok_like[foto_like]>1:
        file_name = f'{foto_id}_{foto_like}_{str(datetime.datetime.now()).split()[0]}'
    else:
        file_name = f'{foto_id}_{foto_like}'
    spisok_foto.append([file_name, foto_url])
    spisok_true.append({'file_name': file_name, 'size': foto_size})
    index += 1
    foto_url=''
    foto_size=''

# ЯНДЕКС ДИСК
yandex_client = YandexAPIClient(yandex_token)   #Создается обьект Яндекс Диск

#4. Проверка - существует ли папка с заданым именем - "{yandex_folder_name}" на яндекс диске? Если ДА то удаляем ее!'
if yandex_client.yandex_info(yandex_folder_name) == 200:
    yandex_client.yandex_delete_folder(yandex_folder_name)
#5. Создаем папку - "{yandex_folder_name}" на Яндекс Диске!
yandex_client.yandex_creet_folder(yandex_folder_name)
#6. Сохраняем фото на Яндекс Диск в папку - "{yandex_folder_name}"!
yandex_client.yandex_save_foto(yandex_folder_name, spisok_foto)

#Сохранение файлов json и txt
#7. Формируется файл "{loadfile}"
with open(loadfile, 'w') as f:
    json.dump(spisok_true, f)

#8. Сохраняется файл "{loadfile}" на Яндекс Диске в папке - {yandex_folder_name}!')
yandex_client.upload_file(loadfile, savefile, replace = True)

#9. Удаляется файл "{loadfile}"
os.remove(loadfile)
