from easy_py_server.easy_server import EasyServer
from evdev import InputDevice, ecodes
import threading
import json
import utils


class CardInputProcessor:
    DEFAULT_CARD_INPUT_DEVICE = '/dev/input/by-id/usb-HXGCoLtd_HIDKeys-event-kbd'

    def __init__(self, device=DEFAULT_CARD_INPUT_DEVICE):
        self.current_card_id = ""
        self.current_card_id_lock = threading.Lock()
        self._inside_visitors_dic = {}
        # init device
        self.dev = InputDevice(device)
        # init database
        self.conn = conn_pool.get_connection()
        self.cur = self.conn.cursor()
        pass

    def working_loop(self):
        last_value = 28
        last_key = None
        card_id = ""
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_KEY:
                key = 28 if event.code == 28 else (event.code - 1) % 10
                if key != last_key:
                    last_key = key
                    last_value = event.value
                else:
                    if last_value == 1 and event.value == 0:
                        if key == 28:  # enter pressed
                            print("ACCESS:" + card_id)
                            curr_time = utils.get_current_time()
                            # persist
                            self.persist_raw_record(card_id, curr_time)
                            if card_id in self._inside_visitors_dic:
                                enter_time = self._inside_visitors_dic.pop(card_id)
                                self.persist_access_record(card_id, enter_time, leave_time=curr_time)
                            else:
                                self._inside_visitors_dic[card_id] = curr_time
                            # FIXME:应该用读写锁优化
                            self.current_card_id_lock.acquire()
                            self.current_card_id = card_id
                            self.current_card_id_lock.release()
                            card_id = ""
                        else:
                            card_id += str(key)
                    last_value = event.value

    def persist_raw_record(self, card_id, time):
        sql = "INSERT INTO raw_record(card_id, time) VALUES (%s, %s) "
        try:
            self.cur.execute(sql, (card_id, time))
            self.conn.commit()
        except:
            pass

    def persist_access_record(self, card_id, enter_time, leave_time):
        sql = "INSERT INTO visitor_stat(card_id, enter_time, leave_time) VALUES (%s, %s, %s) "
        try:
            self.cur.execute(sql, (card_id, enter_time, leave_time))
            self.conn.commit()
        except:
            pass

    def get_current_card_id(self):
        self.current_card_id_lock.acquire()
        card_id = self.current_card_id
        self.current_card_id_lock.release()
        return card_id


# Dao
def query_visitor_stat(last_id, count):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    if last_id != -1:
        sql = "SELECT name,v.card_id,enter_time,leave_time " \
              "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
              "WHERE v.id< %s ORDER BY v.id DESC LIMIT %s"
        cur.execute(sql, (last_id, count))
    else:
        sql = "SELECT name,v.card_id,enter_time,leave_time " \
              "FROM visitor_stat v LEFT JOIN register_visitor r ON v.card_id = r.card_id " \
              "ORDER BY v.id DESC LIMIT %s"
        cur.execute(sql, (count,))
    rst = cur.fetchall()
    cur.close()
    conn_pool.release_conn(conn)
    return rst


def query_raw_record(last_id, count):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    if last_id != -1:
        sql = "SELECT * FROM  raw_record WHERE id< %s ORDER BY id DESC LIMIT %s"
        cur.execute(sql, (last_id, count))
    else:
        sql = "SELECT * FROM  raw_record ORDER BY id DESC LIMIT %s"
        cur.execute(sql, (count,))
    rst = cur.fetchall()
    cur.close()
    conn_pool.release_conn(conn)
    return rst


# Controller
def check_admin_login(session):
    pass


def admin_login(session, param):
    pass


def admin_logout(session, param):
    pass


def change_password(session, param):
    pass


def get_visitor_stat_data_by_count(session, param):
    last_id, count = param['last_id'], param['count']
    rst = query_visitor_stat(int(last_id), int(count))
    return json.dumps(rst, cls=utils.CJsonEncoder)


def get_raw_data_by_count(session, param):
    last_id, count = param['last_id'], param['count']
    rst = query_raw_record(int(last_id), int(count))
    return json.dumps(rst, cls=utils.CJsonEncoder)


def get_register_visitors(session, param):
    pass


def add_register_visitor(session, param):
    pass


def delete_register_visitor(session, param):
    pass


def get_current_card_id(session, param):
    pass


if __name__ == '__main__':
    conn_pool = utils.DBConnectionPool()
    # cardInput = CardInputProcessor()
    # input_thread = threading.Thread(target=cardInput.working_loop, name='input-listen')
    # input_thread.start()
    httpd = EasyServer()
    httpd.get('/api/stat', response_type="application/json; charset=utf-8", listener=get_visitor_stat_data_by_count)
    httpd.get('/api/raw', response_type="application/json; charset=utf-8", listener=get_raw_data_by_count)
    httpd.serve_forever()
    print("bye!")
