from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey

__all__ = ["Category", "Course", "CourseDetail", "Teacher", "DegreeCourse",
           "CourseChapter", "CourseSection", "PricePolicy", "OftenAskedQuestion", "Comment",
           "Account", "CourseOutline", "Coupon", "CouponRecord"]


class Category(models.Model):
    """课程分类"""
    title = models.CharField(max_length=32, unique=True, verbose_name="课程分类")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "01-课程分类"  # 上线删除
        verbose_name_plural = verbose_name = "01-课程分类"


class Course(models.Model):
    """课程表"""
    COURSE_TYPE_CHOICES = ((0, "付费"), (1, "vip专享"), (2, "学位课程"))

    course_type = models.SmallIntegerField(choices=COURSE_TYPE_CHOICES)
    course_img = models.ImageField(upload_to="", verbose_name="课程图片", blank=True, null=True)
    title = models.CharField(max_length=128, unique=128, verbose_name="课程名称")

    category = models.ForeignKey(to="Category", verbose_name="课程的分类")
    degree_course = models.ForeignKey(to="DegreeCourse", null=True, blank=True, help_text="如果是学位课程, 必须关联学位表")

    LEVEL_CHOICES = ((0, "初级"), (1, "中级"), (3, "高级"))
    STATUS_CHOICES = ((0, "上线"), (1, "下线"), (2, "预上线"))
    brief = models.CharField(verbose_name="课程简介", max_length=1024)
    level = models.SmallIntegerField(choices=LEVEL_CHOICES, default=1)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    pub_date = models.DateField(verbose_name="发布日期", blank=True, null=True)

    order = models.IntegerField("课程顺序", help_text="从上一个数据往后排")
    study_num = models.IntegerField(verbose_name="学习人数", help_text="只要有人购买, 订单表加入数据的同时给这个字段+1")

    # 用户反向查找查询, 不生成字段
    price_policy = GenericRelation("PricePolicy")
    often_ask_qeestions = GenericRelation("OftenAskedQuestion")
    course_comments = GenericRelation("Comment")

    def save(self, *args, **kwargs):
        if self.course_type == 2:
            if not self.degree_course:
                raise ValueError("学位课程必须关联学位课程表")
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = verbose_name = "02-课程表"
        db_table = "02-课程表"


class CourseDetail(models.Model):
    """课程详细表"""
    hourse = models.IntegerField(verbose_name="课时", default=7)
    why_study = models.TextField(verbose_name="为什么学习这门课程")
    summary = models.TextField(max_length=2048, verbose_name="课程概述")
    what_to_study_brief = models.TextField(verbose_name="我将学到什么内容")
    vido_brief_link = models.CharField(max_length=255, blank=True, null=True)
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1204)
    career_improvement = models.TextField(verbose_name="此项目如何有助于我的职业生涯")

    course = models.OneToOneField(to="Course")
    recommend_courses = models.ManyToManyField("Course", related_name="recommend_by", blank=True)
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")

    def __str__(self):
        return self.course.title

    class Meta:
        verbose_name_plural = verbose_name = "03-课程详细表"
        db_table = "03-课程详细表"


class Teacher(models.Model):
    """讲师表"""
    name = models.CharField(max_length=32, verbose_name="讲师名字")
    brief = models.TextField(max_length=1024, verbose_name="讲师介绍")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = "04-讲师表"
        db_table = "04-讲师表"


class DegreeCourse(models.Model):
    """
    字段大体跟课程表相同, 哪些不同根据业务逻辑去区分
    """
    title = models.CharField(verbose_name="学位课程", max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = verbose_name = "05-学位课程"
        db_table = "05-学位课程"


class CourseChapter(models.Model):
    """课程章节表"""
    title = models.CharField(max_length=32, verbose_name="课程章节名称")

    course = models.ForeignKey(to="Course", related_name="course_chapters")
    chapter = models.SmallIntegerField(default=1, verbose_name="第几章")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = verbose_name = "06-课程章节表"
        db_table = "06-课程章节表"


class CourseSection(models.Model):
    """课时表"""
    chapter = models.ForeignKey(to="CourseChapter", related_name="course_sections")
    title = models.CharField(max_length=32, verbose_name="课时")
    section_order = models.SmallIntegerField(verbose_name="课时安排", help_text="建议每个课时之间空1至两个值, 以备后续插入课时")
    section_type_choices = ((0, "文档"), (1, "练习"), (2, "视频"))
    section_link = models.CharField(max_length=255, blank=True, null=True, help_text="若是video, 填vid, 若是文档, 填link")
    free_trail = models.BooleanField("是否可试看", default=False)
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices)

    def course_chapter(self):
        return self.chapter.chapter

    def course_name(self):
        return self.chapter.course.title

    class Meta:
        verbose_name_plural = verbose_name = "07-课程课时表"
        db_table = "07-课程课时表"
        unique_together = ("chapter", "section_link")

    def __str__(self):
        return "{}-{}".format(self.course_name(), self.course_chapter())


class PricePolicy(models.Model):
    """价格策略表"""
    content_type = models.ForeignKey(ContentType)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    valid_period_choices = (
        (1, "1天"), (3, "3天"),
        (7, "1周"), (14, "2周"),
        (30, "1个月"), (60, "2个月"),
        (90, "3个月"), (120, "4个月"),
        (180, "6个月"), (210, "12个月"),
        (540, "18个月"), (720, "24个月"),
        (722, "24个月"), (723, "24个月"),
    )
    valid_period = models.SmallIntegerField(choices=valid_period_choices)
    price = models.FloatField()

    def __str__(self):
        return "{}({}){}".format(self.content_object, self.get_valid_period_display(), self.price)

    class Meta:
        verbose_name_plural = verbose_name = "08-价格策略表"
        db_table = "08-价格策略表"
        unique_together = ("content_type", "object_id", "valid_period")


class OftenAskedQuestion(models.Model):
    """常见问题"""
    content_type = models.ForeignKey(ContentType)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1024)

    def __str__(self):
        return "{}-{}".format(self.content_object, self.question)

    class Meta:
        verbose_name_plural = verbose_name = "09-常见问题"
        db_table = "09-常见问题"
        unique_together = ("content_type", "object_id", "question")


class Comment(models.Model):
    """通用评论表"""
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    content = models.TextField(max_length=1024, verbose_name="评论内容")
    account = models.ForeignKey("Account", verbose_name="会员名")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = verbose_name = "10-评论表"
        db_table = "10-通用评论表"


class Account(models.Model):
    """账号信息"""
    username = models.CharField(max_length=32, verbose_name="用户姓名")
    password = models.CharField(max_length=32, verbose_name="用户密码", null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = verbose_name = "11-用户表"
        db_table = "11-用户表"


class Token(models.Model):
    """和账户关联的token值"""
    user = models.OneToOneField(to="Account")
    token = models.CharField(max_length=128)
    # create_time = models.DateTimeField(auto_now_add=True)
    create_time = models.CharField(max_length=128)


class CourseOutline(models.Model):
    """课程大纲"""
    course_detail = models.ForeignKey(to="CourseDetail", verbose_name="课程详细", related_name="course_outline")
    title = models.CharField(max_length=128)
    order = models.PositiveIntegerField(default=1)  # 前端显示顺序

    content = models.TextField("内容", max_length=2048)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        verbose_name_plural = verbose_name = "12-课程大纲"
        db_table = "12-课程大纲"
        unique_together = ("course_detail", "title")


#######################################################################################################

# 支付相关

class Coupon(models.Model):
    """优惠券生成规则"""
    name = models.CharField(max_length=64, verbose_name="活动名称")
    brief = models.TextField(blank=True, null=True, verbose_name="优惠券介绍")
    coupon_type_choice = ((0, "立减券"), (1, "满减券"), (2, "折扣券"))
    coupon_type = models.SmallIntegerField(choices=coupon_type_choice, default=0, verbose_name="券类型")

    money_equivalent_value = models.IntegerField(verbose_name="等值货币", blank=True, null=True)
    off_percent = models.PositiveSmallIntegerField("折扣百分比", help_text="只针对折扣券， 例如7。9折，写79", blank=True, null=True)
    minimum_consume = models.PositiveIntegerField("最低消费", default=0, help_text="仅在满减券时填写此字段")

    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField("绑定课程", blank=True, null=True, help_text="可以把优惠券跟课程绑定")
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField("数量(张)", default=1)
    open_date = models.DateField("优惠券领取开始时间")
    close_date = models.DateField("优惠券领取结束时间")
    valid_begin_date = models.DateField(verbose_name="有效期开始时间", blank=True, null=True)
    valid_end_date = models.DateField(verbose_name="有效结束时间", blank=True, null=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name="优惠券有效期（天）", blank=True, null=True,
                                                    help_text="自券被领时开始算起")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "优惠券生成规则"

    def __str__(self):
        return "{}({})".format(self.get_coupon_type_display(), self.name)


class CouponRecord(models.Model):
    """优惠券发放、消费纪录"""
    coupon = models.ForeignKey("Coupon", on_delete=models.CASCADE)
    user = models.ForeignKey("Account", verbose_name="拥有者", on_delete=models.CASCADE)
    status_choices = ((0, '未使用'), (1, '已使用'), (2, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name="领取时间", help_text="用户领取时间")
    used_time = models.DateTimeField(blank=True, null=True, verbose_name="使用时间")

    class Meta:
        verbose_name_plural = "优惠券发放、消费纪录"

    def __str__(self):
        return '%s-%s-%s' % (self.user, self.coupon, self.get_status_display())
