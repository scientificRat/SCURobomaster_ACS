from typing import Sequence
import conn_pool


# query template
def query(sql, param_tuple=None):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    try:
        if param_tuple is not None:
            cur.execute(sql, param_tuple)
        else:
            cur.execute(sql)
        rst = cur.fetchall()
    except Exception as e:
        print(e)
        return None
    finally:
        cur.close()
        conn_pool.release_conn(conn)
    return rst


def execute_one(sql, param_tuple=None, returning=False):
    rst = None
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    try:
        if param_tuple is not None:
            cur.execute(sql, param_tuple)
        else:
            cur.execute(sql)
        if returning:
            rst = cur.fetchall()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn_pool.release_conn(conn)
    return rst


def check_admin_password(username, password):
    sql = "SELECT COUNT(*) FROM system_admin WHERE user_name=%s AND password=md5(%s)"
    rst = query(sql, (username, password))
    if rst is not None and rst[0][0] > 0:
        return True
    else:
        return False


def update_admin_password(username, old, new):
    sql = "UPDATE system_admin SET password=MD5(%s) WHERE user_name=%s AND password=MD5(%s)"
    execute_one(sql, (new, username, old))


def query_visitor_stat_by_count(last_id, count):
    if last_id != -1:
        sql = "SELECT v.id, v.card_id, name,student_id,college,remark,enter_time,leave_time " \
              "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
              "WHERE v.id< %s ORDER BY v.id DESC LIMIT %s"
        return query(sql, (last_id, count))
    else:
        sql = "SELECT v.id, v.card_id,name,student_id,college,remark,enter_time,leave_time " \
              "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
              "ORDER BY v.id DESC LIMIT %s"
        return query(sql, (count,))


def query_visitor_stat_by_date(start, end):
    sql = "SELECT v.card_id,name,student_id,college,remark,enter_time,leave_time " \
          "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
          "WHERE v.enter_time>=%s AND v.leave_time<=%s ORDER BY v.id DESC"
    return query(sql, (start, end))


def delete_visitor_stat_by_id(ID):
    sql = "DELETE FROM visitor_stat WHERE id = %s RETURNING id"
    rst = execute_one(sql, (ID,), returning=True)
    return len(rst) != 0


def query_raw_record_by_count(last_id, count):
    if last_id != -1:
        sql = "SELECT * FROM  raw_record WHERE id< %s ORDER BY id DESC LIMIT %s"
        return query(sql, (last_id, count))
    else:
        sql = "SELECT * FROM  raw_record ORDER BY id DESC LIMIT %s"
        return query(sql, (count,))


def query_all_register_visitor():
    sql = "SELECT id,card_id,name,student_id,college,remark FROM register_visitor ORDER BY register_time DESC "
    return query(sql)


def query_register_visitors_by_card_id(card_id_list: Sequence[str]):
    sql = "SELECT id,card_id,name,student_id,college,remark FROM register_visitor WHERE card_id = ANY(%s)"
    return query(sql, (card_id_list,))


def add_register_visitor(card_id, name, student_id, college, remark):
    sql = "INSERT INTO register_visitor(card_id, name, student_id, college, remark, register_time) " \
          "VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
    execute_one(sql, (card_id, name, student_id, college, remark))


def delete_register_visitor(ID):
    sql = "DELETE FROM register_visitor WHERE id=%s RETURNING id"
    rst = execute_one(sql, (ID,), returning=True)
    return len(rst) != 0


def persist_raw_record(card_id, time):
    sql = "INSERT INTO raw_record(card_id, time) VALUES (%s, %s) "
    execute_one(sql, (card_id, time))


def persist_access_record(card_id, enter_time, leave_time):
    sql = "INSERT INTO visitor_stat(card_id, enter_time, leave_time) VALUES (%s, %s, %s) "
    execute_one(sql, (card_id, enter_time, leave_time))
