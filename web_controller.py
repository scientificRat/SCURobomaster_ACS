from easy_py_server import Httpd
import utils
import dao
import hardware
import datetime

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


@Httpd.post("/admin/logout", content_type="application/json; charset=utf-8")
def admin_logout(request, response):
    request.removeSession(__ADMIN_SESSION_KEY)
    return utils.JsonHelper.success()


@Httpd.post("/admin/change-password", content_type="application/json; charset=utf-8")
def change_password(request, response):
    old = request.getParam("old_psw")
    new = request.getParam("new_psw")
    username = request.getSession(__ADMIN_SESSION_KEY)
    if username is None:
        return utils.JsonHelper.fail("admin login required")
    if new == "":
        return utils.JsonHelper.fail("password can't be empty")
    if not dao.check_admin_password(username, old):
        return utils.JsonHelper.fail("current password not correct!")
    dao.update_admin_password(username, old, new)
    return utils.JsonHelper.success()


@Httpd.get("/data/visitor-stat/by-count", content_type="application/json; charset=utf-8")
def get_visitor_stat_data_by_count(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    last_id, count = request.getParam('last_id'), request.getParam('count')
    rst = dao.query_visitor_stat_by_count(int(last_id), int(count))
    return utils.JsonHelper.success(rst)


@Httpd.get("/data/visitor-stat/by-date", content_type="application/json; charset=utf-8")
def get_visitor_stat_data_by_date(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    start, end = request.getParam('start'), request.getParam('end')
    rst = dao.query_visitor_stat_by_date(start, end)
    return utils.JsonHelper.success(rst)


@Httpd.get("/data/raw/by-count", content_type="application/json; charset=utf-8")
def get_raw_data_by_count(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    last_id, count = request.getParam('last_id'), request.getParam('count')
    rst = dao.query_raw_record_by_count(int(last_id), int(count))
    return utils.JsonHelper.success(rst)


@Httpd.get("/data/register-visitor/all", content_type="application/json; charset=utf-8")
def get_register_visitors(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    rst = dao.query_all_register_visitor()
    return utils.JsonHelper.success(rst)


@Httpd.post("/add/register-visitor", content_type="application/json; charset=utf-8")
def add_register_visitor(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    card_id = request.getParam("card-id")
    name = request.getParam("name")
    dao.add_register_visitor(card_id, name)
    return utils.JsonHelper.success()


@Httpd.post("/delete/register-visitor", content_type="application/json; charset=utf-8")
def delete_register_visitor(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    ID = request.getParam("id")
    if dao.delete_register_visitor(ID):
        return utils.JsonHelper.success()
    else:
        return utils.JsonHelper.fail("id may not exist")


@Httpd.get("/data/inside-visitor/all", content_type="application/json; charset=utf-8")
def get_inside_visitors(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    inside_visitors_card_id = hardware.get_inside_visitors_card_id()
    rows = dao.query_register_visitors_by_card_id(inside_visitors_card_id)
    known_card_ids = []
    for row in rows:
        known_card_ids.append(row[1])
    for card_id in inside_visitors_card_id:
        if card_id not in known_card_ids:
            rows.append([None, card_id, None])
    return utils.JsonHelper.success(rows)


@Httpd.get("/hardware/current-card-id", content_type="application/json; charset=utf-8")
def get_current_card_id(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    return utils.JsonHelper.success(hardware.get_current_card_id())


@Httpd.post("/hardware/set-mode/importing", content_type="application/json; charset=utf-8")
def set_importing_mode(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    hardware.set_importing_mode()
    return utils.JsonHelper.success()


@Httpd.get("/hardware/last-update-time", content_type="application/json; charset=utf-8")
def get_card_info_updated_time(request, response):
    if not is_admin_login(request):
        return utils.JsonHelper.fail("admin login required")
    time = int((hardware.get_update_time() - datetime.datetime(1970, 1, 1)).total_seconds())
    return utils.JsonHelper.success(time)
