from django.conf.urls import url

from course.view.login import Login
from course.view.course import Course
from course.view.course import CourseChapter
from course.view.course import CourseCategory
from course.view.course import CourseDetailView
from course.view.course import CourseContentView
from course.view.shopping import ShoppingCarView, AccountBalanceView

urlpatterns = [
    # 登陆
    url(r"^login/$", Login.as_view()),

    url(r"^$", Course.as_view()),
    url(r'^coursecategory/$', CourseCategory.as_view()),
    url(r'^coursedetail/(?P<pk>\d+)/$', CourseDetailView.as_view()),
    url(r'^coursechapter/(?P<pk>\d+)/$', CourseChapter.as_view()),
    url(r'^coursecomment/$', CourseContentView.as_view()),

    # 购物车使用认证
    url(r'shoppingcar/$', ShoppingCarView.as_view()),

    # 结算
    url(r'account/$', AccountBalanceView.as_view())
]
