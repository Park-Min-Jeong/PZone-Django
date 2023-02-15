from P_ZONE_NOTICE.settings import MARIADB
import pymysql
import requests
import json


def connectDB(query, foo=False):
    host = MARIADB["default"]["DB_HOST"]
    user = MARIADB["default"]["DB_USER"]
    db = MARIADB["default"]["DB_NAME"]
    password = MARIADB["default"]["DB_PASSWORD"]

    connect = pymysql.connect(host=host, user=user, password=password, port=3306, db=db)
    cursor = connect.cursor()
    cursor.execute(query)

    if foo:
        connect.commit()
        return True
    else:
        return cursor.fetchall()


def whether_gangnam(lat, long):
    dong_list = [row[0] for row in connectDB("SELECT dongcode FROM dong")]
    API = "https://apis.openapi.sk.com/tmap/geo/reversegeocoding?version=1"
    payload = {"appKey": "l7xx0ffb87c22bdb45ae8facaeeb7958ad36", "lon": long, "lat": lat}  # appkey secret 설정 필요
    res = requests.get(API, params=payload)
    dongCode = int(json.loads(res.text)["addressInfo"]["legalDongCode"][5:8])
    if dongCode not in dong_list:
        return False, dongCode
    else:
        return True, dongCode