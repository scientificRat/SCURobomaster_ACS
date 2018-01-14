from typing import Sequence
import evdev  # only some linux(ubuntu,debian...) has this package
import threading
import utils
import dao
import os
import httplib2
import datetime
import time

# singleton

DEFAULT_CARD_INPUT_DEVICE_PATH = '/dev/input/by-id/usb-HXGCoLtd_HIDKeys-event-kbd'

__device_path = DEFAULT_CARD_INPUT_DEVICE_PATH

__current_card_id = ""
__inside_visitors_dic = {}  # card_id ---> enter_time
__dev = None
__importing_mode = False
__mode_lock = threading.Lock()
__update_time = utils.get_current_time()
__audio_client = httplib2.Http()


def start(device_path=DEFAULT_CARD_INPUT_DEVICE_PATH):
    global __dev, __device_path
    # init device
    if __dev is None:
        __device_path = device_path
        __wait_device()
        __connect_device()
        input_thread = threading.Thread(target=__working_loop)
        clean_thread = threading.Thread(target=__clean_loop)  # do cleaning everyday 2:00
        input_thread.start()
        clean_thread.start()
        print("hardware started")


def get_inside_visitors_card_id() -> Sequence[str]:
    return [k for k in __inside_visitors_dic]


def get_current_card_id() -> str:
    return __current_card_id


def set_importing_mode():
    global __importing_mode
    __mode_lock.acquire()
    __importing_mode = True
    __mode_lock.release()


def get_update_time():
    return __update_time


def __wait_device():
    print("finding device... : " + __device_path)
    while True:
        if os.path.exists(__device_path):
            print("device found")
            break


def __connect_device():
    global __dev
    print("connecting to device... ")
    __dev = evdev.InputDevice(__device_path)
    __dev.grab()
    print("device connected")


def __say(text):
    try:
        # 实在没有办法, espeak无法在rc.local 开机启动脚本中正常工作.所以需要在user session 开启后启动一个专门的服务器（不在项目中）
        __audio_client.request("http://localhost:8090/tts?text=" + text)
    except:
        pass


def __working_loop():
    global __current_card_id, __importing_mode, __update_time
    last_value = 28
    last_key = None
    card_id = ""
    while True:
        try:
            for event in __dev.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    key = 28 if event.code == 28 else (event.code - 1) % 10
                    if key != last_key:
                        last_key = key
                        last_value = event.value
                    else:
                        if last_value == 1 and event.value == 0:
                            if key == 28:  # enter pressed
                                print("ACCESS:" + card_id)
                                curr_time = utils.get_current_time()
                                __mode_lock.acquire()
                                if not __importing_mode:
                                    # persist
                                    __persist_raw_record(card_id, curr_time)
                                    if card_id in __inside_visitors_dic:
                                        __say("离开")
                                        enter_time = __inside_visitors_dic.pop(card_id)
                                        __persist_access_record(card_id, enter_time, leave_time=curr_time)
                                    else:
                                        __inside_visitors_dic[card_id] = curr_time
                                        __say("进入")
                                else:
                                    __importing_mode = False
                                __mode_lock.release()
                                __current_card_id = card_id
                                __update_time = curr_time  # I'm not sure if this operation is atomic and thread-safe :)
                                card_id = ""
                            else:
                                card_id += str(key)
                        last_value = event.value
        except OSError as e:
            print(e)
            __say("读卡器,故障")
            __wait_device()
            __connect_device()
            __say("故障排除")


def __clean_loop():
    # do cleaning everyday 2:00
    next_task_time = datetime.datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
    while True:
        curr_time = datetime.datetime.now()
        if curr_time > next_task_time:
            # clean
            for card_id in __inside_visitors_dic:
                enter_time = __inside_visitors_dic.pop(card_id)
                __persist_access_record(card_id, enter_time, leave_time=None)
            next_task_time += datetime.timedelta(days=1)
        else:
            timedelta = next_task_time - curr_time
            time.sleep(timedelta.total_seconds())


def __persist_raw_record(card_id, record_time):
    try:
        dao.persist_raw_record(card_id, record_time)
    except Exception as e:
        print("error", str(utils.get_current_time()), str(e))


def __persist_access_record(card_id, enter_time, leave_time):
    try:
        dao.persist_access_record(card_id, enter_time, leave_time)
    except Exception as e:
        print("error", str(utils.get_current_time()), str(e))
