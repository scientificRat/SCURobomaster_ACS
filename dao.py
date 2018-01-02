import conn_pool


# query template
def query(sql, param_tuple=None):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    if param_tuple is not None:
        cur.execute(sql, param_tuple)
    else:
        cur.execute(sql)
    rst = cur.fetchall()
    cur.close()
    conn_pool.release_conn(conn)
    return rst


def execute_one(sql, param_tuple=None):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    if param_tuple is not None:
        cur.execute(sql, param_tuple)
    else:
        cur.execute(sql)
    conn.commit()
    cur.close()
    conn_pool.release_conn(conn)


def check_admin_password(username, password):
    sql = "SELECT COUNT(*) FROM system_admin WHERE user_name=%s AND password=md5(%s)"
    rst = query(sql, (username, password))
    if rst[0][0] > 0:
        return True
    else:
        return False


def update_admin_password(username, old, new):
    sql = "UPDATE system_admin SET password=MD5(%s) WHERE user_name=%s AND password=MD5(%s)"
    execute_one(sql, (new, username, old))


def query_visitor_stat_by_count(last_id, count):
    if last_id != -1:
        sql = "SELECT name,v.card_id,enter_time,leave_time " \
              "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
              "WHERE v.id< %s ORDER BY v.id DESC LIMIT %s"
        return query(sql, (last_id, count))
    else:
        sql = "SELECT name,v.card_id,enter_time,leave_time " \
              "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
              "ORDER BY v.id DESC LIMIT %s"
        return query(sql, (count,))


def query_visitor_stat_by_date(start, end):
    sql = "SELECT name,v.card_id,enter_time,leave_time " \
          "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
          "WHERE v.enter_time>=%s AND v.leave_time<=%s ORDER BY v.id DESC"
    return query(sql, (start, end))


def query_raw_record_by_count(last_id, count):
    if last_id != -1:
        sql = "SELECT * FROM  raw_record WHERE id< %s ORDER BY id DESC LIMIT %s"
        return query(sql, (last_id, count))
    else:
        sql = "SELECT * FROM  raw_record ORDER BY id DESC LIMIT %s"
        return query(sql, (count,))


def query_all_register_visitor():
    sql = "SELECT * FROM register_visitor ORDER BY register_time DESC "
    return query(sql)


def add_register_visitor(card_id, name):
    sql = "INSERT INTO register_visitor(card_id, name, register_time) VALUES (%s, %s, CURRENT_TIMESTAMP)"
    execute_one(sql, (card_id, name))


def delete_register_visitor(ID):
    sql = "DELETE FROM register_visitor WHERE id=%s RETURNING id"
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    cur.execute(sql, (ID,))
    rst = cur.fetchall()
    cur.close()
    conn_pool.release_conn(conn)
    if len(rst) == 0:
        return False
    else:
        return True
