import time
import hashlib

from rest_framework.views import APIView
from rest_framework.response import Response

from course.models import Account
from course.models import Token
from utils.base_response import BaseResponse


class Login(APIView):
    def get_sercet_str(self, user):
        md5 = hashlib.md5()
        ret = user + str(time.time())
        md5.update(ret.encode("utf-8"))
        return md5.hexdigest()

    def post(self, request):
        res = BaseResponse()

        username = request.data.get("user", "")
        password = request.data.get("pwd", "")
        try:
            user_obj = Account.objects.filter(username=username, password=password).first()
            if not user_obj:
                res.code = 1003
                res.error = "用户名密码错误"
                return Response(res.dict)
            # 获取随机字符串
            sercet_str = self.get_sercet_str(username)
            # 数据库中有这个用户就更新这个token， 没有就创建这个用户和token
            Token.objects.update_or_create(user_id=user_obj.id, defaults={"token": sercet_str})
            res.code = 1001
            res.token = sercet_str
            res.data = {"name": username}
        except Exception as e:
            res.code = 2000
            res.err_msg = str(e)
        return Response(res.dict)
