import time

from django.core.cache import cache

from course.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication


class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 因为中间件的缘故， 复杂请求要跳过，否则会fobbiden
        if request.method == "OPTIONS":
            return

        token = request.META.get("HTTP_TOKEN")
        # 如果没有token
        if not token:
            raise AuthenticationFailed({"code": 1021, "error": "缺少token"})

        # 在缓存中查找token有的化直接判断
        ret = cache.get("token_" + token)
        if ret:
            print("保存到了缓存中了！！！！》》》》》》》》》》》》》》》》")
            return ret, "token_" + token

        # 数据库中获取获取token
        ret_obj = Token.objects.filter(token=token).first()
        if not ret_obj:
            raise AuthenticationFailed({"code": 1022, "error": "认证失败"})
        # 设定存活时间
        # if datetime.datetime.now() - ret_obj.create_time > datetime.timedelta(days=14):
        #     raise AuthenticationFailed("认证失效")

        if time.time() - float(ret_obj.create_time) > 3600 * 24 * 14:
            raise AuthenticationFailed("认证失败")
        # 数据库中查找到token值， 将token值添加到缓存中
        cache_token = "token_" + token

        # delta = datetime.timedelta(days=14) - (datetime.datetime.now() - ret_obj.create_time)
        # delta_num = datetime.timedelta(days=7)
        delta = 3600 * 24 * 14 - (time.time() - float(ret_obj.create_time))
        cache.set(cache_token, ret_obj.user, min(7 * 24 * 3600, delta))

        return ret_obj.user, cache_token
