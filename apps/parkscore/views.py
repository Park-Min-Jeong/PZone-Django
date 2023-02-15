import json
import requests
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator

from haversine import haversine
from datetime import datetime

from apps.home.views import index
# from apps.parkscore.decorators import account_ownership_required
from apps.utils import connectDB, whether_gangnam

from apps.test import *


@login_required
def score(request):
    # Request Post일때
    if request.method == 'POST':
        try:
            long = float(request.POST.get('long'))
            lat = float(request.POST.get('lat'))
        except:
            return redirect("home:nogps")

        img = request.FILES['Camera']

        # 0. 강남구인지 확인
        whether, dongCode = whether_gangnam(lat, long)
        if whether:
            print(dongCode)
        else:
            return redirect("home:notgangnam")
        # dong_list = [row[0] for row in connectDB("SELECT dongcode FROM dong")]
        # API = "https://apis.openapi.sk.com/tmap/geo/reversegeocoding?version=1"
        # payload = {"appKey": "l7xx0ffb87c22bdb45ae8facaeeb7958ad36", "lon": long, "lat": lat}  # appkey secret 설정 필요
        # res = requests.get(API, params=payload)
        # dongCode = int(json.loads(res.text)["addressInfo"]["legalDongCode"][5:8])
        # if dongCode not in dong_list:
        #     return redirect("home:notgangnam")
        # else:
        #     print(dongCode)
        # 강남구가 아니면 다른 페이지로 보내는 작업 추가


        # 1. image
        url = "http://test2-model-svc:8000/file/store/"
        upload = {'file': img}
        image_result = requests.post(url, files=upload).json()  # kickboard, image_distance, uri
        kickboard = image_result["kickboard"]
        image_distance = image_result["image_distance"]
        # kickboard = True
        # image_distance = {"sidewalk": .3, "crosswalk": .2, "braille_block": 1.5, "bike_lane": .5}


        # 2. GPS
        sql = f"""SELECT UNIQUE c.type
                  FROM cautionzone c"""
        gps_distance = {key[0]: [100] for key in connectDB(sql)}

        criteria = 100
        marker_list = []
        # gps_class_list = []
        sql = f"""SELECT c.type, c.name, c.latitude, c.longitude
                  FROM cautionzone c
                  WHERE c.dongcode={dongCode}"""
        for row in connectDB(sql):
            latitude, longitude = float(row[2]), float(row[3])
            distance = haversine((lat, long), (latitude, longitude), unit="m")
            if distance < criteria:
                gps_distance[row[0]].append(distance)
                marker_list.append({"name": row[1], "latitude": latitude, "longitude": longitude})
                # gps_class_list.append(row[0])
        # gps_score = (20 - sum(Counter(gps_class_list).values())) / 5


        # 3. 기울기 sensor
        sensor_score = dict()

        slope_sensor_id = "ea2c64"
        sql = f"""SELECT i.time, i.inc
                  FROM inclination i
                  WHERE i.sen_id='{slope_sensor_id}'
                  ORDER BY i.`time` DESC LIMIT 1"""

        # now = datetime.utcnow()
        sensor_data = connectDB(sql)[0]
        print(sensor_data)
        time_diff = datetime.utcnow() - datetime.strptime(sensor_data[0], "%Y-%m-%d %H:%M:%S")

        if time_diff.seconds < 10:
            sensor_score["angle"] = 0
        else:
            sensor_score["angle"] = 1
        print(time_diff.seconds)


        # 4. final score
        cautions = {"kickboard": 1, "sensor": 1, "image": [], "gps": []}

        weights_dict = {"sidewalk": 5, "crosswalk": 17.6, "braille_block": 8.3, "bike_lane": 4.1,  ## 0 ~ 1.5
                        "bus": 8, "taxi": 8, "subway": 6.6, "fire": 0.1, "children": 1.4}  # 0 ~ 100
        message_dict = {"sidewalk": "보도블럭 중앙", "crosswalk": "횡단보도", "braille_block": "점자블럭", "bike_lane": "자전거도로",
                        "bus": "버스정류장", "taxi": "택시승강장", "subway": "지하철역", "fire": "지상소화전"}

        score = 100

        if kickboard == False:
            score = 0
            cautions["kickboard"] = 0
        elif sensor_score["angle"] == 0:
            score = 0
            cautions["angle"] = 0
        else:
            for key, value in image_distance.items():
                if value < 1.5:
                    temp_score = weights_dict[key] * (1.5 - value) * 20 / 3
                    score = score - temp_score
                    cautions["image"].append(message_dict[key])
            for key, value in gps_distance.items():
                min_value = min(value)
                if min_value < 100:
                    temp_score = weights_dict[key] * (100 - min_value) / 10
                    score = score - temp_score
                    cautions["gps"].append(message_dict[key])

        if score < 0:
            score = 0
        round_score = int(score)


        context = {
            "score": round_score,
            "cautions": cautions,
            "uri": image_result["uri"],
            "lat": lat,
            "long": long,
            "markerList": marker_list,
        }

        return render(request, 'score.html', context)


    ## request method가 Get일때
    else:
        return redirect('home:home')


@login_required
def update(request):
    # 3. 기울기 sensor
    slope_sensor_id = "ea2c64"
    sql = f"""SELECT i.time, i.inc
                      FROM inclination i
                      WHERE i.sen_id='{slope_sensor_id}'
                      ORDER BY i.`time` DESC LIMIT 1"""

    # now = datetime.utcnow()
    sensor_data = connectDB(sql)[0]
    time_diff = datetime.utcnow() - datetime.strptime(sensor_data[0], "%Y-%m-%d %H:%M:%S")

    if time_diff.seconds < 10:
        return redirect("home:angle")
    else:
        sql = f"SELECT av_score FROM score WHERE username = '{request.user.username}'"
        row = connectDB(sql)
        user_score = float(row[0][0])
        round_score = float(request.GET.get('score'))
        gap = (user_score - round_score) / 20
        update_score = round(user_score - gap, 0)

        sql = f"UPDATE `score` SET `av_score`='{update_score}' WHERE  `username`='{request.user.username}';"
        connectDB(sql, foo=True)

        return redirect('home:home')