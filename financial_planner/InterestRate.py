from decimal import Decimal

from financial_planner.DateUnit import DateUnit

class InterestRate:

    def __init__(self, rate):
        self.rate = Decimal(rate)

    def to_dict(self) -> dict:
        return {
            'type': 'interest_rate',
            'rate': str(self.rate),
        }

    @property
    def year(self):
        return self.rate

    @property
    def month(self):
        return self.rate / Decimal("12.0")

    @property
    def week(self):
        return self.rate / Decimal("52.0")

    @property
    def biweek(self):
        return self.rate / Decimal("26.0")

    @property
    def day(self):
        return self.rate / Decimal("365.0")

    def get_rate(self, date_unit: DateUnit) -> Decimal:
        mapping = {
            DateUnit.DAYS: self.day,
            DateUnit.WEEKS: self.week,
            DateUnit.BIWEEK: self.biweek,
            DateUnit.MONTHS: self.month,
            DateUnit.YEARS: self.year,
        }
        return mapping[date_unit]
        