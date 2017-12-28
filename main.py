from easy_py_server.easy_server import EasyServer
from evdev import InputDevice, ecodes
import threading, datetime, psycopg2


def get_current_time():
    return datetime.datetime.now()


class DBConnectionPool:
    def __init__(self):
        self.pool = []
        self.pool_lock = threading.Lock()

    def get_connection(self):
        self.pool_lock.acquire()
        conn = None
        if len(self.pool) == 0:
            try:
                conn = psycopg2.connect(dbname="scu_rm_acs", user="postgres", password="postgres", host="localhost")
            except:
                pass
        else:
            conn = self.pool.pop()
        self.pool_lock.release()
        return conn

    def release_conn(self, conn):
        self.pool_lock.acquire()
        self.pool.append(conn)
        self.pool_lock.release()


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
                            curr_time = get_current_time()
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


def query_visitor_stat(last_id, count):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    if last_id != -1:
        sql = "SELECT * FROM register_visitor AS r NATURAL JOIN visitor_stat AS v WHERE v.id< %s ORDER BY v.id DESC LIMIT %s"
        cur.execute(sql, (last_id, count))
    else:
        sql = "SELECT * FROM register_visitor AS r NATURAL JOIN visitor_stat AS v ORDER BY v.id DESC LIMIT %s"
        cur.execute(sql, (count,))
    rst = cur.fetchall()
    cur.close()
    conn_pool.release_conn(conn)
    return rst


def query_raw_record(last_id, count):
    conn = conn_pool.get_connection()
    cur = conn.cursor()
    if last_id != -1:
        sql = "SELECT * FROM  raw_record WHERE id< %s ORDER BY v.id DESC LIMIT %s"
        cur.execute(sql, (last_id, count))
    else:
        sql = "SELECT * FROM  raw_record ORDER BY v.id DESC LIMIT %s"
        cur.execute(sql, (count,))
    rst = cur.fetchall()
    cur.close()
    conn_pool.release_conn(conn)
    return rst


def get_visitor_stat_data_by_count(session, param):
    last_id, count = param['last_id'], param['count']
    rst = query_visitor_stat(last_id, count)
    return str(rst)


if __name__ == '__main__':
    conn_pool = DBConnectionPool()
    cardInput = CardInputProcessor()
    input_thread = threading.Thread(target=cardInput.working_loop, name='input-listen')
    input_thread.start()
    httpd = EasyServer()
    httpd.get('/api/stat', get_visitor_stat_data_by_count)
    httpd.serve_forever()
    print("bye!")
