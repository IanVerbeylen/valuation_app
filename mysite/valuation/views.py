from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Portfolio

# Create your views here.


class IndexView(generic.ListView):
    template_name = "valuation/index.html"
    context_object_name = "latest_portfolios_list"

    def get_queryset(self):
        """Return the last 5 created portfolios."""
        return Portfolio.objects.filter(creation_date__lte=timezone.now()).order_by(
            "-creation_date"
        )[:5]


class DetailView(generic.DetailView):
    model = Portfolio
    template_name = "valuation/detail.html"

    def get_queryset(self):
        """
        Excludes any portfolios that aren't created yet.
        """
        return Portfolio.objects.filter(creation_date__lte=timezone.now())


class PortfolioReportView(generic.DetailView):
    model = Portfolio
    template_name = "valuation/portfolio_report.html"


def companies(request, portfolio_id):
    response = "You are looking at the companies of portfolio %s"
    return HttpResponse(response % portfolio_id)


def buy_shares(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
    try:
        selected_company = portfolio.company_set.get(pk=request.POST["company"])
    except (KeyError, Portfolio.DoesNotExist):
        # Redisplay the portfolio buying form.
        return render(
            request,
            "valuation/detail.html",
            {"portfolio": portfolio, "error_message": "You didn't select a company."},
        )
    else:
        selected_company.shares += 1
        selected_company.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(
            reverse("portfolio:portfolio_report", args=(portfolio.id,))
        )
