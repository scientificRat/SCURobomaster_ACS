from easy_py_server import Httpd
import utils
import dao

__ADMIN_SESSION_KEY = "admin"


def is_admin_login(request):
    if request.getSession(__ADMIN_SESSION_KEY) is None:
        return False
    return True


@Httpd.post("/admin/login", content_type="application/json; charset=utf-8")
def admin_login(request, response):
    username = request.getParam("username")
    password = request.getParam("password")
    if dao.check_admin_password(username, password):
        request.setSession(__ADMIN_SESSION_KEY, username)
        return utils.JsonHelper.success()
    else:
        return utils.JsonHelper.fail("username or password not correct")


@Httpd.post("/admin/log-out", content_type="application/json; charset=utf-8")
def admin_logout(request, response):
    request.removeSession(__ADMIN_SESSION_KEY)
    return utils.JsonHelper.success()


@Httpd.post("/admin/change-password", content_type="application/json; charset=utf-8")
def change_password(request, response):
    old = request.getParam("old-psw")
    new = request.getParam("new-psw")
    username = request.getSession(__ADMIN_SESSION_KEY)
    if username is None:
        return utils.JsonHelper.fail("admin not login!")
    if not dao.check_admin_password(username, old):
        return utils.JsonHelper.fail("current password not correct!")
    dao.update_admin_password(username, old, new)
    return utils.JsonHelper.success()


@Httpd.get("/data/visitor-stat/by-count", content_type="application/json; charset=utf-8")
def get_visitor_stat_data_by_count(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    last_id, count = request.getParam('last-id'), request.getParam('count')
    rst = dao.query_visitor_stat_by_count(int(last_id), int(count))
    return utils.JsonHelper.to_json(rst)


@Httpd.get("/data/visitor-stat/by-date", content_type="application/json; charset=utf-8")
def get_visitor_stat_data_by_date(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    start, end = request.getParam('start'), request.getParam('end')
    rst = dao.query_visitor_stat_by_date(start, end)
    return utils.JsonHelper.to_json(rst)


@Httpd.get("/data/raw/by-count", content_type="application/json; charset=utf-8")
def get_raw_data_by_count(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    last_id, count = request.getParam('last_id'), request.getParam('count')
    rst = dao.query_raw_record_by_count(int(last_id), int(count))
    return utils.JsonHelper.to_json(rst)


@Httpd.get("/data/register-visitors", content_type="application/json; charset=utf-8")
def get_register_visitors(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    rst = dao.query_all_register_visitor()
    return utils.JsonHelper.to_json(rst)


@Httpd.post("/add/register-visitors", content_type="application/json; charset=utf-8")
def add_register_visitor(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    card_id = request.getParam("card-id")
    name = request.getParam("name")
    dao.add_register_visitor(card_id, name)
    return utils.JsonHelper.success()


@Httpd.post("/delete/register-visitors", content_type="application/json; charset=utf-8")
def delete_register_visitor(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    ID = request.getParam("id")
    if dao.delete_register_visitor(ID):
        return utils.JsonHelper.success()
    else:
        return utils.JsonHelper.fail("id may not exist")


@Httpd.post("/data/current-card-id", content_type="application/json; charset=utf-8")
def get_current_card_id(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    pass
