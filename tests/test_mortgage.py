from decimal import Decimal

import beautiful_date as BD

from financial_planner.Mortgage import compute_payment, MortgagePaymentTransaction, MortgagePrincipal
from financial_planner import ZERO

def test_compute_payment():
    assert(compute_payment(
        Decimal("460000"),
        Decimal("0.0299")/Decimal("12"),
        180,
    ) == Decimal("3174.46"))

def test_payment_cost():
    t = MortgagePaymentTransaction(
        Decimal("460000"),
        Decimal("0.00"),
        180,
        name='a',
        interest_rate="0.0299"
    )
    assert(t.get_cost(BD.D.today()) == ZERO)

def test_principal_cost():
    t = MortgagePrincipal(
        Decimal("460000"),
        Decimal("0.00"),
        180,
        name='a',
        interest_rate="0.0299"
    )
    assert(t.get_cost(BD.D.today()) == ZERO)

    t = MortgagePrincipal(
        Decimal("460000"),
        Decimal("460000"),
        180,
        name='a',
        interest_rate="0.0299"
    )
    assert(t.get_cost(BD.D.today()) < t.payment)