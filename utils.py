import json
import datetime


def get_current_time() -> datetime.datetime:
    return datetime.datetime.now()


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


class JsonHelper:
    @staticmethod
    def to_json(obj):
        return json.dumps(obj, cls=CJsonEncoder)

    @staticmethod
    def success(data=None):
        return JsonHelper.to_json({"success": True, "data": data})

    @staticmethod
    def fail(message=""):
        return JsonHelper.to_json({"success": False, "message": message})
