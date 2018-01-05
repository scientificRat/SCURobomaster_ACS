from easy_py_server import Httpd
import conn_pool
import hardware
import web_controller
import os
import utils

if __name__ == '__main__':
    print("")
    print("**************************************")
    print("[" + utils.get_current_time().ctime() + "]" + " ready to start...")
    print("")
    if os.geteuid() != 0:
        print("This program must be run as root,:)")
        os._exit(0)
    hardware.start()
    conn_pool.start_conn_pool()
    test_conn = conn_pool.get_connection()
    if test_conn is None:
        print("database test fail")
        os._exit(0)
    else:
        conn_pool.release_conn(test_conn)
    Httpd.start_serve(address="0.0.0.0", port=80)
