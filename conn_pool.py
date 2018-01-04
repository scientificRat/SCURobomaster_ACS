import threading
import psycopg2  # support postgres sql

# Singleton
max_connections = 100
__working = False
__dbname = ""
__user = ""
__password = ""
__host, __port = "localhost", 5432
__pool = []
__pool_lock = threading.Lock()


def get_connection():
    __pool_lock.acquire()
    conn = None
    if len(__pool) == 0:
        try:
            conn = psycopg2.connect(dbname=__dbname, user=__user, password=__password, host=__host, port=__port)
        except Exception as e:
            print("[error] connect to database failed, " + str(e))
    else:
        conn = __pool.pop()
    __pool_lock.release()
    return conn


def release_conn(conn):
    if len(__pool) > max_connections:
        conn.close()
    else:
        __pool_lock.acquire()
        __pool.append(conn)
        __pool_lock.release()


def start_conn_pool(dbname="scu_rm_acs", user="postgres", password="postgres", host="localhost", port=5432):
    global __working, __dbname, __user, __password, __host, __port, __pool, __pool_lock
    if not __working:
        __working = True
        __dbname = dbname
        __user = user
        __password = password
        __host = host
        __port = port
        print("Connection pool started")
    else:
        print("connection pool already started!")
    pass
