from dataclasses import dataclass

import numpy_financial as npf
import yfinance as yf
import numpy as np
import pandas as pd


@dataclass
class ModelInputs:
    company_name: str = "Special Purpose Vehicle"
    wacc: float = 0.08
    free_cashflows_last_12_months: float = 500
    growth_short_term: float = 0.05
    growth_long_term: float = 0.02
    n_years_short_term: int = 5
    n_shares: float = 1000
    total_debt_book_value: float = 1000
    cash: float = 3000
    price_per_share: float = 10.5
    marginal_tax_rate: float = 0.25


####################### Request, Load and process data from Yahoo Finance #######################


def request_and_load_yahoo_finance_data(
    ticker: str,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    yearly_inc_stmt = stock.income_stmt
    yearly_bs_stmt = stock.balance_sheet
    yearly_cf_stmt = stock.cashflow
    return (stock_info, yearly_bs_stmt, yearly_inc_stmt, yearly_cf_stmt)


def select_and_process_data_from_financials(
    ticker: str, marginal_tax_rate=0.25
) -> dict:
    (
        stock_info,
        yearly_bs_stmt,
        yearly_inc_stmt,
        yearly_cf_stmt,
    ) = request_and_load_yahoo_finance_data(ticker)

    n_shares = stock_info["floatShares"]
    price_per_share = stock_info["currentPrice"]
    company_name = stock_info["shortName"]

    cash = yearly_bs_stmt.iloc[:, 0]["Cash Cash Equivalents And Short Term Investments"]
    total_debt = (
        yearly_bs_stmt.iloc[:, 0]["Current Debt"]
        + yearly_bs_stmt.iloc[:, 0]["Long Term Debt"]
    )

    revenues = yearly_inc_stmt.iloc[:, 0]["Total Revenue"]
    operating_income = yearly_inc_stmt.iloc[:, 0]["Operating Income"]
    earnings_before_tax = yearly_inc_stmt.iloc[:, 0]["Operating Income"]
    taxes_paid = yearly_inc_stmt.iloc[:, 0]["Pretax Income"]
    effective_tax_rate = taxes_paid / earnings_before_tax

    depreciation_amortization = yearly_cf_stmt.iloc[:, 0][
        "Depreciation And Amortization"
    ]
    capital_expenditures = -yearly_cf_stmt.iloc[:, 0]["Net PPE Purchase And Sale"]
    accounts_receivable_change = yearly_cf_stmt.iloc[:, 0]["Change In Receivables"]
    inventory_change = yearly_cf_stmt.iloc[:, 0]["Change In Inventory"]
    accounts_payable_change = yearly_cf_stmt.iloc[:, 0]["Change In Payable"]

    # processing (to be refactored to own functions)
    working_capital_change = (
        accounts_receivable_change + inventory_change - accounts_payable_change
    )
    net_capex = capital_expenditures - depreciation_amortization
    free_cashflow = (
        operating_income * (1 - marginal_tax_rate) - net_capex - working_capital_change
    )
    # currently, marginal_tax_rate is hardcoded. The tax rate to use is user discretion, so
    # there should be user inputs to fintune model assumptions like marginal vs effective tax rate.
    # This pushes processing to own functions, with user inputs if user want customization.

    return {
        "n_shares": n_shares,
        "price_per_share": price_per_share,
        "company_name": company_name,
        "cash": cash,
        "total_debt": total_debt,
        "revenues": revenues,
        "operating_income": operating_income,
        "effective_tax_rate": effective_tax_rate,
        "depreciation_amortization": depreciation_amortization,
        "capital_expenditures": capital_expenditures,
        "working_capital_change": working_capital_change,
        "free_cashflow": free_cashflow,
    }


# def process_working_capital_change(ticker: str) -> dict:
#     financials_dict = select_data_from_financials(ticker)
#     working_capital_change = (
#         financials_dict['accounts_receivable_change']
#         + financials_dict['inventory_change']
#         - financials_dict['accounts_payable_change']
#     )
#     return working_capital_change


def initialize_yahoo_finance_inputs(ticker: str) -> ModelInputs:
    # ModelInputs atm, can be own dataclass
    financials_dict = select_and_process_data_from_financials(ticker)
    yahoo_data = ModelInputs(
        company_name=financials_dict["company_name"],
        free_cashflows_last_12_months=financials_dict["free_cashflow"],
        n_shares=financials_dict["n_shares"],
        total_debt_book_value=financials_dict["total_debt"],
        cash=financials_dict["cash"],
        price_per_share=financials_dict["price_per_share"],
        growth_short_term=0.05,
    )
    return yahoo_data


############################## Simplified Financial Model ##############################


def project_cashflows(data: ModelInputs = None) -> list[float]:
    current_cashflow = data.free_cashflows_last_12_months
    short_term_growth = data.growth_short_term
    years = data.n_years_short_term
    projected_cashflows = [
        current_cashflow * (1 + short_term_growth) ** year for year in range(years)
    ]
    return projected_cashflows


def terminal_value_from_final_projected_cashflow(data: ModelInputs) -> float:
    projected_cashflows = project_cashflows(data)
    last_projected_cashflow = projected_cashflows[-1]
    terminal_cashflow = last_projected_cashflow * (1 + data.growth_long_term)
    terminal_value = terminal_cashflow / (data.wacc - data.growth_long_term)
    return terminal_value


def add_terminal_value_to_projected_cashflows(data: ModelInputs) -> list[float]:
    projected_cashflows = project_cashflows(data)
    terminal_value = terminal_value_from_final_projected_cashflow(data)
    total_cashflows = projected_cashflows[:-1] + [
        projected_cashflows[-1] + terminal_value
    ]
    return total_cashflows


def discount_projected_cashflows(data: ModelInputs) -> list[float]:
    total_cashflows = add_terminal_value_to_projected_cashflows(data)
    discounted_cashflows = npf.npv(data.wacc, total_cashflows)
    return discounted_cashflows


def equity_market_value_from_enterprise_value(data: ModelInputs) -> float:
    discounted_cashflows = discount_projected_cashflows(data)
    enterprise_value = discounted_cashflows
    equity_market_value = enterprise_value - data.total_debt_book_value + data.cash
    return equity_market_value


def value_per_share_from_equity_market_value(data: ModelInputs) -> float:
    equity_market_value = equity_market_value_from_enterprise_value(data)
    value_per_share = equity_market_value / data.n_shares
    return value_per_share


def value_price_ratio_from_value_per_share(data: ModelInputs) -> float:
    value_per_share = value_per_share_from_equity_market_value(data)
    value_price_ratio = value_per_share / data.price_per_share - 1
    return value_price_ratio


def is_undervalued(data: ModelInputs) -> bool:
    value_price_ratio = value_price_ratio_from_value_per_share(data)
    undervalued = True if value_price_ratio > 0 else False
    return undervalued


def display_value_price_ratio_message(data: ModelInputs) -> None:
    value_price_ratio = value_price_ratio_from_value_per_share(data)
    undervalued = is_undervalued(data)
    if undervalued:
        print(
            f"The shares of {data.company_name} are {value_price_ratio:.2%} undervalued."
        )
    else:
        print(
            f"The shares of {data.company_name} are {value_price_ratio:.2%} overvalued."
        )


def display_valuation_report(
    ticker: str = None, data: ModelInputs = None, print_output: bool = False
) -> float:
    """
    Takes a ticker or a ModelInputs instance as an input and prints a valuation report.
    If no ModelInputs dataclass is provided, the ticker input is sent to the yahoo finance API
    and a ModelInputs instance is created.
    """
    if data is None:
        data = initialize_yahoo_finance_inputs(ticker)
    value_per_share = value_per_share_from_equity_market_value(data)
    if print_output:
        print(f"***** {data.company_name} - valuation report: *****")
        print(f"Value per share: €{value_per_share:,.2f}")
        print(f"Price per share: €{data.price_per_share:,.2f}")
        display_value_price_ratio_message(data)
