from django.http import HttpResponse
from django.shortcuts import render

from resumee.models import Resumee
from resumee.serializers import ResumeeSerializer


def generate_cv(request, *args, **kwargs):
    active_resumee = Resumee.objects.filter(active=True).first()
    cv_data = ResumeeSerializer(active_resumee).data
    return render(request, f"cv/{active_resumee.template.name}", cv_data)
