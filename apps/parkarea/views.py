from django.shortcuts import render
import requests
import json
import time
from apps.utils import connectDB


def parkmap(request):
    # 현재 위치
    longitude = float(request.GET.get('long'))
    latitude = float(request.GET.get('lat'))

    sql = """SELECT p.type, p.name, p.latitude, p.longitude
             FROM parkingzone p"""

    url = f"https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"
    headers = {
        "appkey": "l7xx0ffb87c22bdb45ae8facaeeb7958ad36 ",
    }

    minTime = 1000000000000
    for row in connectDB(sql):
        time.sleep(0.1)
        payload = {
            "startX": longitude,
            "startY": latitude,
            "endX": row[3],
            "endY": row[2],
            "startName": "현위치",
            "endName": "주차장"
        }

        res = requests.post(url, json=payload, headers=headers)

        jsonObj = json.loads(res.text)

        if jsonObj["features"][0]["properties"]["totalTime"] < minTime:
            nearest = jsonObj
            minTime = jsonObj["features"][0]["properties"]["totalTime"]

    context = {
        "nearest": nearest
    }

    return render(request, 'parkmap.html', context)