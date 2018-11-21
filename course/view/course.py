import uuid

from rest_framework.views import APIView
from rest_framework.response import Response

from course import models
from course.serializers import CourseCategorySerializer
from course.serializers import CourseSerializer
from course.serializers import CourseDetailSerializer
from course.serializers import CourseChapterSerializer
from course.serializers import CourseCommentSerializer
from course.serializers import UserSerializer
from course.models import Account
# 导入BaseResponse
from utils.base_response import BaseResponse
# 认证
from utils.authentications import UserAuthentication


class CourseCategory(APIView):
    """课程分类"""

    def get(self, request):
        queryset = models.Category.objects.all()
        ser_obj = CourseCategorySerializer(queryset, many=True)
        return Response(ser_obj.data)


class Course(APIView):
    """课程"""
    # authentication_classes = [UserAuthentication, ]

    def get(self, request):
        cartegory_id = request.query_params.get("category", "0")
        if cartegory_id == "0":
            queryset = models.Course.objects.all().order_by("-order")
        else:
            queryset = models.Course.objects.filter(category_id=cartegory_id).order_by("-order")

        ser_obj = CourseSerializer(queryset, many=True)
        return Response(ser_obj.data)


class CourseDetailView(APIView):
    """课程详细页面"""

    def get(self, request, pk):
        course_detail_obj = models.CourseDetail.objects.filter(course_id=pk).first()
        if not course_detail_obj:
            return Response({"code": 1001, "errors": "不存在这门课程"})
        ser_obj = CourseDetailSerializer(course_detail_obj)
        return Response(ser_obj.data)


class CourseChapter(APIView):
    """课程章节"""

    def get(self, request, pk):
        queryset = models.CourseChapter.objects.filter(course_id=pk)
        ser_obj = CourseChapterSerializer(queryset, many=True)
        return Response(ser_obj.data)


class CourseContentView(APIView):
    """课程评论"""

    def get(self, request):
        queryset = models.Comment.objects.all()
        ser_obj = CourseCommentSerializer(queryset, many=True)
        return Response(ser_obj.data)


class UserView(APIView):

    # 注册用户
    def post(self, request):
        res = BaseResponse()
        ser_obj = UserSerializer(data=request.data)
        if ser_obj.is_valid():
            ser_obj.save()
            res.data = ser_obj.validated_data
        else:
            res.code = 1010
            res.data = ser_obj.errors
        return Response(res.dict)


class LoginView(APIView):
    # 登录视图
    def post(self, request):
        res = BaseResponse()
        # 获取用户的密码
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user_obj = Account.objects.filter(username=username, password=password).first()
        if not user_obj:
            res.code = 1003
            res.error = "用户名或密码错误"
        try:
            token = uuid.uuid4()
            # user_obj_queryset.update(token=token)
            user_obj.token.objects.update(token=token)
            res.data = token
        except Exception as e:
            res.code = 1004
            res.error = "生成token失败"
        return Response(res.dict)



