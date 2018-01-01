from easy_py_server import Httpd
import conn_pool
import web_controller
# import hardware

if __name__ == '__main__':
    # cardInput = CardInputProcessor()
    # input_thread = threading.Thread(target=cardInput.working_loop, name='input-listen')
    # input_thread.start()
    conn_pool.start_conn_pool()
    Httpd.start_serve()
