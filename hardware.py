from evdev import InputDevice, ecodes  # only some linux(ubuntu,debian...) has this package
from typing import Sequence
import threading
import utils
import dao

# singleton
DEFAULT_CARD_INPUT_DEVICE = '/dev/input/by-id/usb-HXGCoLtd_HIDKeys-event-kbd'

__current_card_id = ""
__current_card_id_lock = threading.Lock()
__inside_visitors_dic = {}  # card_id ---> enter_time
__dev = None


def start(device=DEFAULT_CARD_INPUT_DEVICE):
    global __dev
    # init device
    if __dev is None:
        __dev = InputDevice(device)
        input_thread = threading.Thread(target=__working_loop, name='input-listen')
        input_thread.start()
        print("Hardware started")


def get_current_card_id() -> str:
    __current_card_id_lock.acquire()
    card_id = __current_card_id
    __current_card_id_lock.release()
    return card_id


def get_inside_visitors_card_id() -> Sequence[str]:
    return [k for k in __inside_visitors_dic]


def __working_loop():
    global __current_card_id
    last_value = 28
    last_key = None
    card_id = ""
    for event in __dev.read_loop():
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
                        __persist_raw_record(card_id, curr_time)
                        if card_id in __inside_visitors_dic:
                            enter_time = __inside_visitors_dic.pop(card_id)
                            __persist_access_record(card_id, enter_time, leave_time=curr_time)
                        else:
                            __inside_visitors_dic[card_id] = curr_time
                        # TODO:可以用读写锁优化
                        __current_card_id_lock.acquire()
                        __current_card_id = card_id
                        __current_card_id_lock.release()
                        card_id = ""
                    else:
                        card_id += str(key)
                last_value = event.value


def __persist_raw_record(card_id, time):
    try:
        dao.persist_raw_record(card_id, time)
    except Exception as e:
        print("error", str(utils.get_current_time()), str(e))
        pass


def __persist_access_record(card_id, enter_time, leave_time):
    try:
        dao.persist_access_record(card_id, enter_time, leave_time)
    except Exception as e:
        print("error", str(utils.get_current_time()), str(e))
