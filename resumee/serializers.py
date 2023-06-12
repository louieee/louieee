import random

from rest_framework import serializers

from resumee.models import Resumee, WorkExperience, Education, Skill, Portfolio, Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"


class PortfolioSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Portfolio
        fields = "__all__"

    def get_images(self, obj):
        return obj.images

    def get_image(self, obj):
        if obj.images:
            return random.choice(obj.images)
        return None


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        exclude = ("order",)


class WorkExperienceSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = WorkExperience
        fields = "__all__"

    def get_skills(self, obj):
        return SkillSerializer(Skill.objects.filter(id__in=obj.skills), many=True).data

    def get_descriptions(self, obj):
        return obj.descriptions

    def get_duration(self, obj):
        return obj.duration

    def get_start_date(self, obj):
        return obj.start_date.strftime('%b %Y')

    def get_end_date(self, obj):
        if obj.end_date is not None:
            return obj.end_date.strftime('%b %Y')
        return "Present"


class EducationSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = "__all__"

    def get_duration(self, obj):
        return obj.duration

    def get_start_date(self, obj):
        return obj.start_date.strftime('%b %Y')

    def get_end_date(self, obj):
        if obj.end_date is not None:
            return obj.end_date.strftime('%b %Y')
        return "Present"


class ResumeeSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    work_history = serializers.SerializerMethodField()
    education_history = serializers.SerializerMethodField()
    portfolios = PortfolioSerializer(many=True)
    work_completed = serializers.SerializerMethodField(read_only=True)
    years_of_exp = serializers.SerializerMethodField(read_only=True)
    total_clients = serializers.SerializerMethodField(read_only=True)
    profile_pic = serializers.SerializerMethodField(read_only=True)
    languages = LanguageSerializer(many=True)

    class Meta:
        model = Resumee
        fields = "__all__"

    def get_skills(self, obj):
        return SkillSerializer(obj.skills, many=True).data
    
    def get_profile_pic(self, obj):
        return obj.profile_url

    def get_work_history(self, obj):
        return WorkExperienceSerializer(obj.work_history.all().order_by("end_date"), many=True).data

    def get_education_history(self, obj):
        return EducationSerializer(obj.education_history.all().order_by("end_date"), many=True).data

    def get_work_completed(self, obj):
        return obj.portfolios.count()

    def get_years_of_exp(self, obj):
        return obj.years_of_experience

    def get_total_clients(self, obj):
        return obj.number_of_clients
