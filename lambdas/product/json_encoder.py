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


# class JSONEncoder(json.JSONEncoder):
#
#     def default(self, obj):
#         if isinstance(obj, decimal.Decimal):
#             return {
#                 "__type__": "Decimal",
#                 "value": str(obj),
#             }
#         if isinstance(obj, datetime.datetime):
#             return {
#                 "__type__": "datetime",
#                 "value": [
#                     obj.year,
#                     obj.month,
#                     obj.day,
#                     obj.hour,
#                     obj.minute,
#                     obj.second,
#                 ],
#             }
#         if isinstance(obj, datetime.date):
#             return {
#                 "__type__": "date",
#                 "value": [obj.year, obj.month, obj.day],
#             }
#         if isinstance(obj, datetime.time):
#             return {
#                 "__type__": "time",
#                 "value": [obj.hour, obj.minute, obj.second],
#             }
#         return super().default(obj)


# class JSONDecoder(json.JSONDecoder):
#     @classmethod
#     def object_hook(cls, obj):
#         for key in obj:
#             if isinstance(key, six.string_types):
#                 if 'type{decimal}' == key:
#                     try:
#                         return decimal.Decimal(obj[key])
#                     except:
#                         pass
#
#     def __init__(self, **kwargs):
#         kwargs['object_hook'] = self.object_hook
#         super(CommonJSONDecoder, self).__init__(**kwargs)

# class JSONDecoder(json.JSONDecoder):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(object_hook=self.object_hook, *args,  **kwargs)
#
#     def object_hook(self, obj):
#         v = obj.get("__type__")
#         if v is None:
#             return obj
#         if v == "Decimal":
#             return decimal.Decimal(obj["value"])
#         if v == "datetime":
#             return datetime.datetime(*obj["value"])
#         if v == "date":
#             return datetime.date(*obj["value"])
#         if v == "time":
#             return datetime.time(*obj["value"])
#         raise TypeError(f"Unserializable object {obj} of type {type(obj)}")
