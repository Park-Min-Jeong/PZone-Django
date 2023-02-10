import json
from collections import Counter
import requests

from django.shortcuts import render, redirect
from django.urls import reverse

from haversine import haversine
from datetime import datetime

from apps.home.views import index
from apps.utils import connectDB


def score(request):
    # Request Post일때
    if request.method == 'POST':
        long = float(request.POST.get('long'))
        lat = float(request.POST.get('lat'))
        img = request.FILES['Camera']
        print(lat, long)

        # 0. 강남구인지 확인
        dong_list = [row[0] for row in connectDB("SELECT dongcode FROM dong")]
        API = "https://apis.openapi.sk.com/tmap/geo/reversegeocoding?version=1"
        payload = {"appKey": "l7xx0ffb87c22bdb45ae8facaeeb7958ad36", "lon": long, "lat": lat}  # appkey secret 설정 필요
        res = requests.get(API, params=payload)
        dongCode = int(json.loads(res.text)["addressInfo"]["legalDongCode"][5:8])
        if dongCode not in dong_list:
            print("여기는 강남구가 아님")
        else:
            print("여기는 강남구")
            print(dongCode)
        # 강남구가 아니면 다른 페이지로 보내는 작업 추가


        # 1. image
        url = "http://18.177.143.210:8080/file/store/"
        upload = {'file': img}
        image_result = requests.post(url, files=upload).json()


        # 2. GPS
        # 전체 개수로 판정
        # 알고리즘 수정 필요
        criteria = 200
        marker_list = []
        gps_class_list = []
        sql = f"""SELECT c.type, c.name, c.latitude, c.longitude
                  FROM cautionzone c
                  WHERE c.dongcode={dongCode}"""
        for row in connectDB(sql):
            latitude, longitude = float(row[2]), float(row[3])
            distance = haversine((lat, long), (latitude, longitude), unit="m")
            if distance < criteria:
                print(distance)
                marker_list.append({"name": row[1], "latitude": latitude, "longitude": longitude})
                gps_class_list.append(row[0])
        # gps_score = (20 - sum(Counter(gps_class_list).values())) / 5


        # 3. 기울기 sensor
        sensor_score = dict()

        slope_sensor_id = "ea2b62"
        sql = f"""SELECT i.time, i.inc
                  FROM inclination i
                  WHERE i.sen_id='{slope_sensor_id}'
                  ORDER BY i.`time` DESC LIMIT 1"""

        # now = datetime.utcnow()
        sensor_data = connectDB(sql)[0]
        time_diff = datetime.utcnow() - datetime.strptime(sensor_data[0], "%Y-%m-%d %H:%M:%S")

        if time_diff.seconds < 10:
            sensor_score["angle"] = 0
        else:
            sensor_score["angle"] = 2


        # 4. final score
        cautions = dict()
        score = 0

        if image_result["kickboard"] == False:
            cautions["kickboard"] = "none"
        else:
            # gps
            cautions["gps"] = list(Counter(gps_class_list).keys())
            score = score + (20 - sum(Counter(gps_class_list).values())) / 5

            # image
            temp = []
            for k, v in image_result["image_score"].items():
                score = score + v
                if v < 1:  # 1 - max_distance
                    temp.append(k)
            cautions["image"] = temp

            # sensor
            temp = []
            for k, v in sensor_score.items():
                score = score + v
                if v < 1:
                    temp.append(k)
            cautions["sensor"] = temp

        context = {
            "score": round(score, 1),
            "cautions": cautions,
            "uri": image_result["uri"],
            "lat": lat,
            "long": long,
            "markerList": marker_list,
        }

        return render(request, 'score.html', context)


    ## request method가 Get일때
    else:
        return reverse(index)