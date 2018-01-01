from evdev import InputDevice, ecodes  # only some linux(ubuntu,debian...) has this package
import threading
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
        self.conn = utils.conn_pool.get_connection()
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
