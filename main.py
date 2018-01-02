from easy_py_server import Httpd
import conn_pool
import hardware
import web_controller

if __name__ == '__main__':
    hardware.start()
    conn_pool.start_conn_pool()
    Httpd.start_serve()
