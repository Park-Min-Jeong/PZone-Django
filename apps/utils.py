from P_ZONE_NOTICE.settings import MARIADB
import pymysql


def connectDB(query):
    host = MARIADB["default"]["DB_HOST"]
    user = MARIADB["default"]["DB_USER"]
    db = MARIADB["default"]["DB_NAME"]
    password = MARIADB["default"]["DB_PASSWORD"]

    connect = pymysql.connect(host=host, user=user, password=password, port=3306, db=db)
    cursor = connect.cursor()
    cursor.execute(query)

    return cursor.fetchall()