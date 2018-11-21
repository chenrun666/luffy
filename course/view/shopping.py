import json
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
from django.core.exceptions import ObjectDoesNotExist

from course.models import Course
from course.models import CouponRecord

from utils.base_response import BaseResponse
from utils.exceptions import PricePolicyNotExist
from utils.authentications import UserAuthentication

"""
购物车
redis 的数据接口设计
redis = {
    shopping_car_<user_id>_<course_id>: {
        "id": course.id, 带用户id是为了用户查看购物车的时候需要
        "title": course.name,
        "img": str(course.course_img)
        "policy_dict": {
            policy_id: {
                "period": item.valid_period, 价格策略
                "period_display": item.get_valid_period_display(),
                "price": item.price, 价格
            }，
            policy_id2: {
                ...
            }
        },
        "default_policy": policy_id 选择的价格策略id
        
    }
}
"""


class ShoppingCarView(APIView):
    def __init__(self):
        self.r = get_redis_connection("default")
        super(ShoppingCarView, self).__init__()

    """
    购物车接口
    1010 代表成功
    1011 课程不存在
    1012 价格策略不存在
    1013 获取购物处失败
    1014 删除的购物车数据不存在
    """

    authentication_classes = [UserAuthentication, ]

    def trans_str(self, all_keys):
        back_list = []
        for item in all_keys:
            query_key = item.decode("utf-8")
            back_data = self.r.hgetall(query_key)
            course_name = Course.objects.filter(id=back_data[b'course_id'].decode("utf-8")).first().title
            back_dict = {
                "price_dict": json.loads(back_data[b'price_dict']),
                "course_name": course_name,
                "default_price_policy_id": back_data[b'default_price_policy_id'].decode("utf-8")
            }
            back_list.append(back_dict)
        return back_list

    # 展示购物车数据
    def get(self, request, *args, **kwargs):
        """
        展示购物车数据，需要商品名称， 价格， 价格策略， 周期
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        res = BaseResponse()
        # 初始化一个对象
        user_id = request.user.id
        r_key = "shoppingcar_{}_{}".format(user_id, "*")
        all_keys = self.r.scan_iter(r_key)
        if not all_keys:
            res.msg = "购物车为空"
            res.code = 1030
            return Response(res.dict)

        # 构建返回前段的数据结构
        # back_list = []
        # for item in all_keys:
        #     query_key = item.decode("utf-8")
        #     back_data = self.r.hgetall(query_key)
        #     course_name = Course.objects.filter(id=back_data[b'course_id'].decode("utf-8")).first().title
        #     back_dict = {
        #         "price_dict": json.loads(back_data[b'price_dict']),
        #         "course_name": course_name,
        #         "default_price_policy_id": back_data[b'default_price_policy_id'].decode("utf-8")
        #     }
        #     back_list.append(back_dict)
        back_list = self.trans_str(all_keys)

        res.code = 1031
        res.data = back_list

        return Response(res.dict)

    def post(self, request, *args, **kwargs):
        """
        给购物车增加数据，
        传过来的数据有 课程ID以及价格策略
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        # 获取提交的数据
        res = BaseResponse()
        data = request.data
        course_id = data.get("course_id")
        price_policy_id = data.get("price_policy_id")
        user_id = request.user.id
        # 校验数据
        # 课程数据
        try:
            course_obj = Course.objects.get(id=course_id)

            # 校验价格策略
            price_obj = course_obj.price_policy.all()
            # 循环构建价格策略的数据结构
            price_dict = {}
            for price in price_obj:
                price_dict[price.id] = {
                    "price": price.price,
                    "valid_period": price.valid_period,
                    "valid_period_id": price.get_valid_period_display(),
                }
            # 判断价格是否存在
            if price_policy_id not in price_dict:
                raise PricePolicyNotExist("价格不存在")

            # 价格存在的话， 保存到redis中
            r_key = "shoppingcar_{}_{}".format(user_id, course_id)
            value = {
                "course_id": course_id,
                "course_title": course_obj.title,
                "default_price_policy_id": price_policy_id,
                "price_dict": json.dumps(price_dict),
            }
            self.r.hmset(r_key, value)
            res.data = "添加购物车成功"

        except ObjectDoesNotExist:
            res.code = 1001
            res.error = "课程不存在"
        except PricePolicyNotExist as e:
            res.code = 1010
            res.error = str(e)

        return Response(res.dict)

    def put(self, request):
        # 初始化一个res
        res = BaseResponse()
        # 获取用户id
        user_id = request.user.id
        course_id = request.data.get("course_id")
        price_policy_id = request.data.get("price_policy_id")

        redis_key = "shoppingcar_{}_{}".format(user_id, course_id)
        all_keys = self.r.exists(redis_key)
        # 判断购物车是否有这个商品
        if not all_keys:
            res.code = 1044
            res.error = "购物车没有该课程"
            return Response(res.dict)
        all_keys = self.r.scan_iter(redis_key)
        # 将获取到的bytes类型转换为字符串类型
        str_value = self.trans_str(all_keys)[0]

        # 判断发送的价格策略是否在数据库中的价格策略中
        if str(price_policy_id) not in str_value["price_dict"]:
            res.code = 1045
            res.msg = "没有这个价格策略"
            return Response(res.dict)

        # # 修改redis中的数据, 重新构建redis中的数据格式， 注意json.dumps
        str_value["default_price_policy_id"] = price_policy_id
        str_value.pop("course_name")
        str_value["course_id"] = course_id
        str_value["price_dict"] = json.dumps(str_value["price_dict"])

        self.r.hmset(redis_key, str_value)
        res.msg = "修改成功"
        return Response(res.dict)

    def delete(self, request):
        # 初始化res
        res = BaseResponse()
        # 获取课程id
        course_id = request.data.get("course_id")
        redis_key = "shoppingcar_{}_{}".format(request.user.id, course_id)
        if not self.r.exists(redis_key):
            res.error = "课程不存在， 删除失败"
            return Response(res.dict)
        self.r.delete(redis_key)
        res.msg = "删除成功"
        return Response(res.dict)


class AccountBalanceView(APIView):
    authentication_classes = [UserAuthentication]

    def __init__(self):
        self.r = get_redis_connection()
        super(AccountBalanceView, self).__init__()

    def tran_str(self, dic):
        after_dic = {}
        for key, value in dic.items():
            try:
                ret = json.loads(dic[key].decode("utf-8"))
                after_dic[key.decode("utf-8")] = ret
            except Exception as e:
                after_dic[key.decode("utf-8")] = dic[key].decode("utf-8")
        return after_dic

    def tran_json(self, dic):
        after_dic = {}
        for key, value in dic.items():
            try:
                after_dic[key] = json.dumps(value)
            except Exception as e:
                after_dic[key] = value
        return after_dic

    def get_coupon_info(self, request, course_id=None):
        now = datetime.datetime.now()
        coupon_info = CouponRecord.objects.filter(
            user=request.user,
            coupon__content_type_id=10,
            coupon__object_id=course_id,
            coupon__valid_begin_date__lte=now,
            coupon__valid_end_date__gte=now,
        )
        # 获取到的知识优惠券对象， 不能传递到前端使用，需要重新构建数据结构
        # 初始化一个优惠券字典
        course_coupon_info = {}
        for info in coupon_info:
            course_coupon_info[info.id] = {
                "name": info.coupon.name,
                "valid_end_date": info.coupon.get_coupon_type_display(),
                "coupon_type": info.coupon.get_coupon_type_display(),
                "minimum_consume": info.coupon.minimum_consume,
                "money_equivalent_value": info.coupon.money_equivalent_value,
                "off_percent": info.coupon.off_percent,
            }
        return course_coupon_info

    def post(self, request):
        # 初始化一个响应对象
        res = BaseResponse()

        # 接受数据， 课程id， 获得的是个列表
        course_id = request.data.get("course_id")
        # 获取用户ID
        user_id = request.user.id
        # 在购物车中（redis）校验课程id是否存在
        for course_id in course_id:
            # 初始化一个课程信息字典
            course_info = {}
            shoppingcar = "shoppingcar_{}_{}".format(user_id, course_id)
            shoppingcar = self.r.hgetall(shoppingcar)
            # 如果不存在， 返回错误信息
            if not shoppingcar:
                res.code = 1051
                res.error = "课程不存在购物车中"
                return Response(res.dict)
            shoppingcar_str = self.tran_str(shoppingcar)
            # course_info["course_info"] = json.dumps(shoppingcar_str)
            # 获取优惠券信息
            # 通过用户对象查找到和用户相关的所有优惠券,
            # 区分课程优惠券，通用优惠券
            # 查抄条件：1， 用户对象， 2， content_type，3 相关课程
            #  4，是否在有效期内
            course_coupon_info = self.get_coupon_info(request, course_id=course_id)

            # 获取通用优惠券
            gengeal_coupon_info = self.get_coupon_info(request)
            gengeal_coupon_info_json = self.tran_json(gengeal_coupon_info)

            # 将获取到的课程信息， 课程优惠券信息， 通用优惠券保存到redis中。
            self.r.hmset("accountcoupon_{}_{}".format(user_id, course_id), {"course_info": json.dumps(shoppingcar_str),
                                                                            "course_coupon_info": json.dumps(
                                                                                course_coupon_info),
                                                                            })
            self.r.hmset("gengeal_{}".format(user_id), gengeal_coupon_info_json)

        res.msg = "添加结算成功"
        res.data = 1050
        return Response(res.dict)

    def get(self, request):
        res = BaseResponse()
        try:
            user_id = request.user.id
            course_coupon_key = "accountcoupon_{}_*".format(user_id)
            gengeal_coupon_key = "gengeal_{}".format(user_id)
            clear_informations = self.r.scan_iter(course_coupon_key)
            back_info = {}
            for key in clear_informations:
                detail_info = self.r.hgetall(key)
                detail_info_str = self.tran_str(detail_info)
                # back_info.append(detail_info_str)
                back_info["detail_info"] = detail_info_str
            gengeal_coupon_info = self.r.hgetall(gengeal_coupon_key)
            gengeal_coupon_info_str = self.tran_str(gengeal_coupon_info)
            # print(gengeal_coupon_info_str)
            print(back_info)
            back_info["gengeal_info"] = gengeal_coupon_info_str
            res.data = back_info
        except Exception as e:
            res.code = 1061
            res.error = str(e)

        return Response(res.dict)
