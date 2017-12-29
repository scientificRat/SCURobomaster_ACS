import json
import datetime
import threading
import psycopg2


def get_current_time():
    return datetime.datetime.now()


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


class JsonHelper:
    @staticmethod
    def toJson(obj):
        return json.dumps(obj, cls=CJsonEncoder)

    @staticmethod
    def success(data=None):
        return JsonHelper.toJson({"success": True, "data": data})

    @staticmethod
    def fail(self, message=""):
        return JsonHelper.toJson({"success": False, "message": message})


class DBConnectionPool:
    def __init__(self, dbname="scu_rm_acs", user="postgres", password="postgres", host="localhost", port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.pool = []
        self.pool_lock = threading.Lock()

    def get_connection(self):
        self.pool_lock.acquire()
        conn = None
        if len(self.pool) == 0:
            try:
                conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host,
                                        port=self.port)
            except:
                pass
        else:
            conn = self.pool.pop()
        self.pool_lock.release()
        return conn

    def release_conn(self, conn):
        self.pool_lock.acquire()
        self.pool.append(conn)
        self.pool_lock.release()
