from easy_py_server.easy_server import EasyServer

if __name__ == '__main__':
    httpd = EasyServer()
    httpd.serve_forever()