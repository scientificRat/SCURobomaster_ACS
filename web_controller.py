from easy_py_server import Httpd
import utils
from dao import *


@Httpd.get("/admin/login", content_type="application/json; charset=utf-8")
def admin_login(request, response):
    username = request.getParam("username")
    password = request.getParam("password")
    sql = "SELECT COUNT(*) FROM administrator WHERE user_name=%s AND password=MD5(%s)"
    rst = query(sql, (username, password))
    request.setSession("admin", username)
    return utils.JsonHelper.success(rst)


@Httpd.get("/admin/change-password", content_type="application/json; charset=utf-8")
def admin_logout(request, response):
    request.removeSession("admin")
    response.setContentType("application/json; charset=utf-8")
    return utils.JsonHelper.success()


@Httpd.get("/admin/change-password", content_type="application/json; charset=utf-8")
def change_password(request, response):
    username = request.getSession("admin")
    if username is None:
        return utils.JsonHelper.fail("Admin not login!")
    old = request.getParam("old_psw")
    new = request.getParam("new_psw")
    sql = "UPDATE administrator SET password=MD5(%s) WHERE user_name=%s AND password=%s"
    execute_one(sql, (new, username, old))
    # TODO: NOT FINISHED
    return utils.JsonHelper.success()


@Httpd.get("/data/stat", content_type="application/json; charset=utf-8")
def get_visitor_stat_data_by_id(request, response):
    last_id, count = request.getParam('last_id'), request.getParam('count')
    rst = query_visitor_stat_by_id(int(last_id), int(count))
    return utils.JsonHelper.toJson(rst)


@Httpd.get("/data/raw", content_type="application/json; charset=utf-8")
def get_raw_data_by_count(request, response):
    last_id, count = request.getParam('last_id'), request.getParam('count')
    rst = query_raw_record_by_id(int(last_id), int(count))
    return utils.JsonHelper.toJson(rst)


@Httpd.get("/data/register-visitors", content_type="application/json; charset=utf-8")
def get_register_visitors(request, response):
    pass


@Httpd.post("/add/register-visitors", content_type="application/json; charset=utf-8")
def add_register_visitor(request, response):
    pass


@Httpd.post("/delete/register-visitors", content_type="application/json; charset=utf-8")
def delete_register_visitor(request, response):
    pass


@Httpd.post("/data/current-card-id", content_type="application/json; charset=utf-8")
def get_current_card_id(request, response):
    pass
