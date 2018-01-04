from easy_py_server import Httpd
import conn_pool
import hardware
import web_controller
import os

if __name__ == '__main__':
    hardware.start()
    conn_pool.start_conn_pool()
    test_conn = conn_pool.get_connection()
    if test_conn is None:
        print("database test fail")
        os._exit(0)
    else:
        conn_pool.release_conn(test_conn)
    Httpd.start_serve(port=80)
