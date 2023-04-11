from decimal import Decimal

from beautiful_date import *

from financial_planner.TaxRate import ConstantTaxRate, IncomeTaxRate
from financial_planner.common import ZERO

def test_constant():
    rate = ConstantTaxRate("0.10")
    assert(Decimal("10.00") == rate.get_additional_taxes(Decimal("100.00"), None))

def test_income():
    rate = IncomeTaxRate()
    assert(ZERO == rate.get_additional_taxes(Decimal("21000.00"), 10/Apr/2023))
    taxes = rate.get_additional_taxes(Decimal("2000.00"), 10/Apr/2023)
    assert(Decimal("0.12") * Decimal("1000.00") == taxes)
    rate.get_additional_taxes(Decimal("65450.00"), 11/Apr/2023)
    taxes = rate.get_additional_taxes(Decimal("2000.00"), 12/Apr/2023)
    assert(
        Decimal("0.12") * Decimal("1000.00") + Decimal("0.22") * Decimal("1000.00")\
        == taxes
    )
    rate.get_additional_taxes(Decimal("692750.00"), 11/Apr/2024)
    taxes = rate.get_additional_taxes(Decimal("2000.00"), 12/Apr/2024)
    assert(
        Decimal("0.35") * Decimal("1000.00") + Decimal("0.37") * Decimal("1000.00")\
        == taxes
    )