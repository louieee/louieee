from django.shortcuts import render

from resumee.models import Resumee, Portfolio
from resumee.serializers import ResumeeSerializer, PortfolioSerializer


# Create your views here.


def home(request, *args, **kwargs):
    active_resumee = Resumee.objects.filter(active=True).first()
    cv_data = ResumeeSerializer(active_resumee).data
    return render(request, "resumee/index.html", cv_data)


def portfolio_detail(request, *args, **kwargs):
    portfolio_id = kwargs.get("id")
    data = PortfolioSerializer(Portfolio.objects.get(id=portfolio_id)).data
    return render(request, "resumee/portfolio-details.html", data)
