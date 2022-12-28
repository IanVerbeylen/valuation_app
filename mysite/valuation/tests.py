import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse


from .models import Portfolio

# Create your tests here.


class PortfolioModelTests(TestCase):
    def test_was_created_recently_with_future_portfolio(self):
        """
        was_created_recently() returns False for portfolios whose
        creation_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_portfolio = Portfolio(creation_date=time)
        self.assertIs(future_portfolio.was_created_recently(), False)

    def test_was_created_recently_with_old_portfolio(self):
        """
        was_created_recently() returns False for portfolios whose
        creation_date is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_portfolio = Portfolio(creation_date=time)
        self.assertIs(old_portfolio.was_created_recently(), False)

    def test_was_created_recently_with_recent_portfolio(self):
        """
        was_created_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_portfolio = Portfolio(creation_date=time)
        self.assertIs(recent_portfolio.was_created_recently(), True)


def create_portfolio(portfolio_name, days) -> Portfolio:
    """
    Create a portfolio with the given 'portfolio_name' and with created the given number
    of 'days' offset to now (negative for portfolios created in the past, positive
    for portfolios that have yet to be created).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Portfolio.objects.create(portfolio_name=portfolio_name, creation_date=time)


class PortfolioIndexViewTests(TestCase):
    def test_no_portfolios(self):
        """
        if no portfolios exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("portfolio:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No portfolios were created.")
        self.assertQuerysetEqual(response.context["latest_portfolios_list"], [])

    def test_past_portfolio(self):
        """
        Portfolios with a creation_date in the past are displayed on the index page.
        """
        portfolio = create_portfolio(portfolio_name="Old portfolio", days=-30)
        response = self.client.get(reverse("portfolio:index"))
        self.assertQuerysetEqual(
            response.context["latest_portfolios_list"], [portfolio]
        )

    def test_future_portfolio(self):
        """
        Portfolios with a creation_date in the future aren't displayed on the index page.
        """
        portfolio = create_portfolio(portfolio_name="Future portfolio", days=30)
        response = self.client.get(reverse("portfolio:index"))
        self.assertQuerysetEqual(response.context["latest_portfolios_list"], [])

    def test_future_portfolio_and_past_portfolio(self):
        """
        Even if both past and future portfolios exist, only past portfolios
        are displayed.
        """
        portfolio = create_portfolio(portfolio_name="Past portfolio.", days=-30)
        create_portfolio(portfolio_name="Future portfolio.", days=30)
        response = self.client.get(reverse("portfolio:index"))
        self.assertQuerysetEqual(
            response.context["latest_portfolios_list"],
            [portfolio],
        )

    def test_two_past_portfolios(self):
        """
        The portfolios index page may display multiple portfolios.
        """
        portfolio1 = create_portfolio(portfolio_name="Past portfolio 1.", days=-30)
        portfolio2 = create_portfolio(portfolio_name="Past portfolio 2.", days=-5)
        response = self.client.get(reverse("portfolio:index"))
        self.assertQuerysetEqual(
            response.context["latest_portfolios_list"],
            [portfolio2, portfolio1],
        )

    class PortfolioDetailViewTests(TestCase):
        def test_future_portfolio(self):
            """
            The detail view of a portfolio with a creation_date in the future
            returns a 404 not found.
            """
            future_portfolio = create_portfolio(
                portfolio_name="Future portfolio", days=5
            )
            url = reverse("valuation:detail", args=(future_portfolio.id,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

        def test_past_portfolio(self):
            """
            The detail view of a portfolio with a creation_date in the past
            displays the portfolio's name.
            """
            past_portfolio = create_portfolio(portfolio_name="Past Portfolio", days=-5)
            url = reverse("valuation:detail", args=(past_portfolio.id,))
            response = self.client.get(url)
            self.assertEqual(response, past_portfolio.portfolio_name)
