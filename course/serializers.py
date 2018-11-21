import hashlib

from rest_framework import serializers

from . import models


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id", "title"]


class CourseSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source="get_level_display")
    price_policy = serializers.SerializerMethodField()

    def get_price_policy(self, obj):
        for price in obj.price_policy.all():
            return price.price

    class Meta:
        model = models.Course
        fields = ["id", "title", "course_img",
                  "category", "level", "study_num",
                  "price_policy", "brief"]


class CourseDetailSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source="course.get_level_display")
    study_num = serializers.IntegerField(source="course.study_num")

    price_policy = serializers.SerializerMethodField()
    course_outline = serializers.SerializerMethodField()
    recommend_courses = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()

    def get_price_policy(self, obj):
        return [{"id": price_obj.id, "valid_price_display": price_obj.get_valid_period_display(),
                 "price": price_obj.price} for price_obj in obj.course.price_policy.all()]

    def get_course_outline(self, obj):
        outlines = obj.course_outline.all().order_by("order")
        return [{"title": outline.title, "content": outline.content} for outline in outlines]

    def get_recommend_courses(self, obj):
        return [{"id": item.id, "title": item.title} for item in obj.recommend_courses.all()]

    def get_teachers(self, obj):
        return [{"id": item.id, "name": item.name} for item in obj.teachers.all()]

    class Meta:
        model = models.CourseDetail
        fields = ["id", "summary", "hourse", "level", "study_num",
                  "price_policy", "why_study", "what_to_study_brief",
                  "course_outline", "career_improvement", "prerequisite",
                  "recommend_courses", "teachers"]


class CourseChapterSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    def get_sections(self, obj):
        sections = obj.course_sections.all().order_by("section_order")
        return [{"id": item.id, "title": item.title} for item in sections]

    class Meta:
        model = models.CourseChapter
        fields = ["id", "title", "chapter", "course", "sections"]


class CourseCommentSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source="account.username")

    class Meta:
        model = models.Comment
        fields = ["id", "account", "content", "date"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data["password"]
        password_salt = password + "luffy"
        md5_str = hashlib.md5(password_salt.encode()).hexdigest()
        user_obj = models.Account.objects.create(username=validated_data["username"], password=md5_str)
        return user_obj
