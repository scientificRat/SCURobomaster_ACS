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


def query_visitor_stat_by_id(last_id, count):
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


def query_raw_record_by_id(last_id, count):
    if last_id != -1:
        sql = "SELECT * FROM  raw_record WHERE id< %s ORDER BY id DESC LIMIT %s"
        return query(sql, (last_id, count))
    else:
        sql = "SELECT * FROM  raw_record ORDER BY id DESC LIMIT %s"
        return query(sql, (count,))


def query_all_register_visitor():
    sql = "SELECT * FROM register_visitor ORDER BY register_time DESC "
    return query(sql)
