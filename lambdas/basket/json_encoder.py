import json
import decimal
import datetime
import time


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        if isinstance(obj, datetime.date):
            return str(obj)
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, time.struct_time):
            return datetime.datetime.fromtimestamp(time.mktime(obj))
        # Any other serializer
        return super(JSONEncoder, self).default(obj)

