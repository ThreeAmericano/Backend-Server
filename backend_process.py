#-*-coding:utf-8-*-
'''

    [ BackEnd Processing Program ]

작성일 : 2021-08-10
작성자 : 최현식(chgy2131@naver.com)

변경점
    - 최초작성

'''

import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from module.rabbitmq import rabbitmq_clinet
from module.weather_api import weather_api

