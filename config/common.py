import requests
import platform
import time
import datetime
import uuid
import hmac
import hashlib
import os
import random

default_agent = {
    'sdkVersion': 'python/4.2.0',
    'osPlatform': platform.platform() + " | " + platform.python_version()
}


def generate_verification_code():
    return str(random.randint(1000000, 9999999))

def get_url(path):
    # 솔라피 기본 API URL
    base_url = 'https://api.solapi.com'  # 솔라피 API의 기본 URL
    
    # API 키와 Secret을 포함한 인증을 위한 헤더 설정
    url = base_url + path  # path를 기본 URL에 추가
    return url  # 최종 URL 반환


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def get_signature(key='', msg=''):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

def get_headers(api_key='', api_secret_key=''):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {
        'Authorization': 'HMAC-SHA256 ApiKey=' + api_key + ', Date=' + date + ', salt=' + salt + ', signature=' +
                         get_signature(api_secret_key, data),
        'Content-Type': 'application/json; charset=utf-8'
    }

def send_one(data):
    data['agent'] = default_agent
    return requests.post(get_url('/messages/v4/send-many/detail'),
                         headers=get_headers(
                             os.getenv('SO_ACCESS'), 
                             os.getenv('SO_SECRET')
                            ),
                         json=data)