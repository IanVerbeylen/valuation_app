from django.urls import path

from . import views

app_name = "portfolio"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:portfolio_id>/companies/", views.companies, name="companies"),
    path("<int:portfolio_id>/buy_shares/", views.buy_shares, name="buy_shares"),
    path(
        "<int:pk>/portfolio_report/",
        views.PortfolioReportView.as_view(),
        name="portfolio_report",
    ),
]
