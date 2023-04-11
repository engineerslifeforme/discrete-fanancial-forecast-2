from decimal import Decimal
from dataclasses import dataclass

import beautiful_date as BD

from financial_planner.InterestRate import InterestRate
from financial_planner.common import CENTS, ZERO, month_int, parse_date
from financial_planner.TaxRate import TaxRatePrototype, ConstantTaxRate

@dataclass
class TransactionLog:
    source: str
    destination: str
    title: str
    amount: Decimal
    date: BD.BeautifulDate

    def to_dict(self) -> dict:
        return {
            'source': self.source,
            'destination': self.destination,
            'title': self.title,
            'amount': self.amount,
            'date': self.date,
        }

class TransactionPrototype:
    subtype = 'transaction'

    def __init__(
        self,
        name: str = None,
        amount = None,
        interest_rate = None,
        start_date = None,
        end_date = None,
        every_x_periods: int = 1,
        tax_rate: TaxRatePrototype = None) -> None:
        assert(name is not None), "All transactions must have a name"
        assert(amount is not None), "All transactions must have an amount"
        self.name = name
        self.amount = Decimal(amount).quantize(CENTS)
        if interest_rate is None:
            self.interest_rate = InterestRate(Decimal("0.00"))
        else:
            self.interest_rate = InterestRate(interest_rate)
        if start_date is None:
            self.start_date = BD.D.today()
        else:
            if type(start_date) == BD.BeautifulDate:
                self.start_date = start_date
            else:
                self.start_date = parse_date(start_date)
        self.end_date = end_date
        if end_date is not None:
            if type(end_date) != BD.BeautifulDate:
                self.end_date = parse_date(end_date)
        self.every_x_periods = every_x_periods
        if tax_rate is None:
            self.tax_rate = ConstantTaxRate()
        else:
            self.tax_rate = tax_rate

    def to_dict(self) -> dict:
        return {
            'type': 'transaction',
            'subtype': self.subtype,
            'name': self.name,
            'amount': str(self.amount),
            'interest_rate': self.interest_rate.to_dict(),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'every_x_periods': self.every_x_periods,
        }
    
    def active(self, date) -> bool:
        not_active = date < self.start_date
        if self.end_date is not None:
            not_active |= date > self.end_date
        return not not_active

    def get_cost(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> Decimal:
        if not self.active(date):
            return ZERO
        else:
            return self._get_active_cost(date, relative_date)

    def get_tax(self, date: BD.BeautifulDate, taxed_amount: Decimal) -> Decimal:
        return self.tax_rate.get_additional_taxes(taxed_amount, date)

    def current_value(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> Decimal:
        return (self.amount * (1 + self.interest_rate.day * (date - relative_date).days)).quantize(CENTS)

class DailyTransaction(TransactionPrototype):
    subtype = 'daily'

    def _get_active_cost(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> Decimal:        
        if (date - self.start_date).days % self.every_x_periods == 0:
            return self.current_value(date, relative_date)
        else:
            return ZERO

class WeeklyTransaction(DailyTransaction):
    subtype = 'weekly'

    def __init__(self, *args, every_x_periods: int = 1, **kwargs) -> None:
        super().__init__(*args, every_x_periods=every_x_periods*7, **kwargs)

class BiWeeklyTransaction(WeeklyTransaction):
    subtype = 'biweekly'

    def __init__(self, *args, every_x_periods: int = 1, **kwargs) -> None:
        super().__init__(*args, every_x_periods=every_x_periods*2, **kwargs)

class MonthlyTransaction(TransactionPrototype):
    subtype = 'monthly'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert(self.start_date.day <= 28), f"Monthly transactions must start on day 1-28, {self.name} starts on {self.start_date.day}"

    def _get_active_cost(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> Decimal:
        if date.day == self.start_date.day:
            if (month_int(date) - month_int(self.start_date)) % self.every_x_periods == 0:
                return self.current_value(date, relative_date)
            else:
                return ZERO
        else:
            return ZERO

class YearlyTransaction(MonthlyTransaction):
    subtype = 'yearly'

    def __init__(self, *args, every_x_periods: int = 1, **kwargs) -> None:
        super().__init__(*args, every_x_periods=every_x_periods*12, **kwargs)


