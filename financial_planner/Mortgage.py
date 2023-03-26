""" Mortgage creation"""

from decimal import Decimal
import math

import beautiful_date as BD

from financial_planner.InterestRate import InterestRate
from financial_planner.Account import Debt
from financial_planner.Transaction import MonthlyTransaction
from financial_planner.common import ZERO, CENTS



def compute_payment(principal: Decimal, interest: Decimal, terms: int) -> Decimal:
    result = Decimal((float(principal)*float(interest))/(1-math.pow((1+float(interest)), (-1 * float(terms))))).quantize(CENTS)
    return result

class Mortgage(Debt):
    def calculate_interest(self, *args) -> Decimal:
        return ZERO


class MortgagePaymentTransaction(MonthlyTransaction):

    def __init__(self, loan_amount: Decimal, remaining_balance: Decimal, terms: int, extra_principal: Decimal = ZERO, **kwargs) -> None:
        super().__init__(amount=ZERO, **kwargs)
        assert(self.end_date is None), f"Mortgages cannot have an end date ({self.name})"
        self.remaining_balance = Decimal(remaining_balance)
        self.payment = compute_payment(Decimal(loan_amount), self.interest_rate.month, int(terms)) + Decimal(extra_principal)

    @property
    def interest_payment(self) -> Decimal:
        return Decimal(self.interest_rate.month * self.remaining_balance).quantize(CENTS)

    @property
    def principal_payment(self) -> Decimal:
        return self.payment - self.interest_payment

    @property
    def return_value(self) -> Decimal:
        return self.payment * Decimal("-1")

    @staticmethod
    def calculate_payoff(remainder: Decimal) -> Decimal:
        return remainder

    def current_value(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> Decimal:
        if self.remaining_balance <= ZERO:
            return ZERO
        if self.remaining_balance > self.payment:
            self.remaining_balance -= self.principal_payment
            return self.return_value
        else:
            value = self.calculate_payoff(self.remaining_balance)
            self.remaining_balance = ZERO
            return value


    def _get_active_cost(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> Decimal:
        if date.day == self.start_date.day:
            return self.current_value(date, relative_date)
        else:
            return ZERO

class MortgagePrincipal(MortgagePaymentTransaction):

    @property
    def return_value(self) -> Decimal:
        return self.principal_payment

    @staticmethod
    def calculate_payoff(remainder: Decimal) -> Decimal:
        return Decimal("-1.00") * remainder


def create_mortgage_transactions():
    pass