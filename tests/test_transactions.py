from decimal import Decimal

from beautiful_date import *

from financial_planner import DailyTransaction, MonthlyTransaction, ZERO, YearlyTransaction

def test_amount_format():
    # Test different versions of amount
    for amount_type in [5, Decimal("5.00"), "5.00", 5.0]:
        daily = DailyTransaction('a', amount_type)
        cost = daily.get_cost(D.today())
        assert(cost == Decimal("5.00"))

def test_dates():
    daily = DailyTransaction('a', 5, start_date=1/Mar/2023)
    assert(daily.get_cost(1/Feb/2023) == ZERO)

    daily = DailyTransaction('a', 5, end_date=1/Mar/2030)
    assert(daily.get_cost(2/Mar/2030) == ZERO)

def test_alternating():
    daily = DailyTransaction('a', 5, every_x_periods=2)
    assert(daily.get_cost(D.today() + (1 * days)) == ZERO)
    assert(daily.get_cost(D.today() + (2 * days)) == Decimal("5.00"))

    monthly = MonthlyTransaction('a', 5, every_x_periods=2)
    assert(monthly.get_cost(D.today() + (1 * months)) == ZERO)
    assert(monthly.get_cost(D.today() + (2 * months)) == Decimal("5.00"))

def test_monthly_transaction():
    monthly = MonthlyTransaction('a', 5)
    assert(monthly.get_cost(12/Feb/2023) == ZERO)
    assert(monthly.get_cost(11/Mar/2023) == Decimal("5.00"))

def test_interest_rate():
    daily = DailyTransaction('a', 5, interest_rate=0.05)
    cost = daily.get_cost(D.today() + (1 * years))
    assert(cost == Decimal("5.25"))

def test_start_date():
    yearly = YearlyTransaction('a', 5, start_date=15/Dec/2023)

    