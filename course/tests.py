from django.test import TestCase

# Create your tests here.


import redis

"""
连接方式
连接池
操作
    String
    Hash
    List
    Set
    Sort Set
管道
发布订阅
"""

# r = redis.Redis(host="127.0.0.1", port=6379)
# r.set('foo', 'bar')
# print(r.get('foo'))


# import datetime
#
# now = datetime.datetime.now()
# print(now)
# d1 = now - datetime.timedelta(hours=1)
# print(d1)

# import hashlib, time
#
# md5 = hashlib.md5()
#
# md5.update(str(time.time()).encode("utf-8"))
# print(md5.hexdigest())
#
# print(time.time())

# dic = {b'default_price_policy_id': b'1', b'course_title': b'python\xe5\x85\xa8\xe6\xa0\x88\xe8\xaf\xbe\xe7\xa8\x8b', b'price_dict': b'{"2": {"price": 100.0, "valid_period": 120, "valid_period_id": "4\\u4e2a\\u6708"}, "3": {"price": 40000.0, "valid_period": 180, "valid_period_id": "6\\u4e2a\\u6708"}, "1": {"price": 10000.0, "valid_period": 722, "valid_period_id": "24\\u4e2a\\u6708"}}', b'course_id': b'1'}
# import json
# def tran_str(dic):
#     after_dic = {}
#     for key, value in dic.items():
#         try:
#             ret = json.loads(dic[key].decode("utf-8"))
#             after_dic[key.decode("utf-8")] = ret
#         except Exception as e:
#             after_dic[key.decode("utf-8")] = dic[key].decode("utf-8")
#
#     return after_dic



