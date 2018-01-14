import psycopg2.pool as pool

# Singleton
__conn_pool = None


def get_connection():
    return __conn_pool.getconn()


def release_conn(conn):
    return __conn_pool.putconn(conn)


def start_conn_pool(dbname="scu_rm_acs", user="postgres", password="postgres", host="localhost", port=5432):
    global __conn_pool
    if __conn_pool is None:
        __conn_pool = pool.ThreadedConnectionPool(5, 100, dbname=dbname, user=user, password=password, host=host,
                                                  port=port)
        print("Connection pool started")
    else:
        print("connection pool already started!")
    pass
