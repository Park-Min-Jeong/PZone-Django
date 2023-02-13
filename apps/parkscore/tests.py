# from django.test import TestCase
# from apps.utils import connectDB
from P_ZONE_NOTICE.settings import MARIADB
import pymysql

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
sql = "SELECT * FROM score WHERE username='asdf'"
print(connectDB(sql))