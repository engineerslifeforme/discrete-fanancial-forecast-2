from decimal import Decimal

import beautiful_date as BD

from financial_planner.common import ZERO

class TaxRatePrototype:
    tax_type = 'prototype'

    def __init__(self):
        pass

    def get_additional_taxes(self, untaxed_amount: Decimal, date: BD.BeautifulDate) -> Decimal:
        raise(NotImplementedError())
    
    def get_amount_tax(self, total: Decimal) -> tuple:
        raise(NotImplementedError())
    
    def to_dict(self) -> dict:
        return {
            'type': self.tax_type,
        }

class ConstantTaxRate(TaxRatePrototype):
    tax_type = 'constant'

    def __init__(self, rate: str = "0.00"):
        self.rate = Decimal(rate)

    def get_additional_taxes(self, untaxed_amount: Decimal, date: BD.BeautifulDate) -> Decimal:
        """ Additional amount to withdraw for taxes

        :param untaxed_amount: amount needed excluding taxes
        :type untaxed_amount: Decimal
        :return: additional amount to withdraw for taxs
        :rtype: Decimal
        """
        return untaxed_amount * self.rate
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            'rate': self.rate,
        })
        return base
    
# 2023 Tax Brackets
# https://www.irs.gov/newsroom/irs-provides-tax-inflation-adjustments-for-tax-year-2023

TAX_BRACKETS = [
    (ZERO, ZERO),
    (Decimal("22000.00"), Decimal("0.12")),
    (Decimal("89450.00"), Decimal("0.22")),
    (Decimal("190750.00"), Decimal("0.24")),
    (Decimal("364200.00"), Decimal("0.32")),
    (Decimal("462500.00"), Decimal("0.35")),
    (Decimal("693750.00"), Decimal("0.37")),
]
    
class IncomeTaxRate(ConstantTaxRate):
    tax_type = 'income'

    def __init__(self, bank):
        self.bank = bank
        self.year = None

    @property
    def balance(self) -> Decimal:
        return self.bank.get_year_balance(self.year)

    @property
    def rate(self) -> Decimal:
        """ Get tax rate based on balance

        :return: tax rate
        :rtype: Decimal

        Do not use when spanning bands
        """
        _, rate = self.get_band_rate()
        return rate
    
    def in_band(self, lower_limit: Decimal, upper_limit: Decimal) -> bool:
        """ Check if in band

        :param lower_limit: income over limit
        :type lower_limit: Decimal
        :param upper_limit: applies until this amount
        :type upper_limit: Decimal
        :return: true in band, false not in band
        :rtype: bool

        "incomes over $X are taxed at Y"
        """
        if self.balance == ZERO and lower_limit == ZERO:
            return True
        return self.balance > lower_limit and self.balance <= upper_limit

    def get_next_band(self, index: int) -> tuple:
        """ Get data for next band

        :param index: band index
        :type index: int
        :return: tuple of rate of brack above, starting limit of bracket above, remaining until bracket above
        :rtype: tuple
        """
        try:
            upper_income_limit, upper_rate = TAX_BRACKETS[index]
            remaining_to_limit = upper_income_limit - self.balance
        except IndexError:
            upper_income_limit, upper_rate = TAX_BRACKETS[-1]
            remaining_to_limit = None
        return upper_rate, upper_income_limit, remaining_to_limit
    
    def get_band_rate(self) -> tuple:
        """ Determines rate based on balance

        :return: remaining and rate to use
        :rtype: tuple
        """
        lower_income_limit, lower_rate = TAX_BRACKETS[0]
        upper_income_limit, upper_rate = TAX_BRACKETS[1]
        remaining_to_limit = upper_income_limit - self.balance
        index = 1
        while not self.in_band(lower_income_limit, upper_income_limit) and remaining_to_limit is not None:
            index += 1
            lower_rate, lower_income_limit = upper_rate, upper_income_limit
            upper_rate, upper_income_limit, remaining_to_limit = self.get_next_band(index)
            
        
        if remaining_to_limit == ZERO:
            index += 1
            lower_rate, lower_income_limit = upper_rate, upper_income_limit
            upper_rate, upper_income_limit, remaining_to_limit = self.get_next_band(index)

        return remaining_to_limit, lower_rate
    
    @property
    def remaining_band(self) -> Decimal:
        remaining_band, _ = self.get_band_rate()
        return remaining_band
    
    def get_additional_taxes(self, untaxed_amount: Decimal, date: BD.BeautifulDate) -> Decimal:
        """ Generates taxes on an amount based on tax bracket for year

        :param untaxed_amount: amount needed
        :type untaxed_amount: Decimal
        :param date: date of withdrawal
        :type date: BD.BeautifulDate
        :return: taxes incurred
        :rtype: Decimal
        """
        if self.year is None:
            self.year = date.year
        elif date.year != self.year:
            self.year = date.year
        
        do_not_split = False
        taxes = None
        if self.remaining_band is None:
            do_not_split = True
        if not do_not_split:
            if untaxed_amount > self.remaining_band:
                initial_amount = self.remaining_band
                taxes = self.get_additional_taxes(initial_amount, date)
                taxes += self.get_additional_taxes(untaxed_amount - initial_amount, date)
        if taxes is None:
            taxes = super().get_additional_taxes(untaxed_amount, date)
        return taxes
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.pop('rate')
        return base
    
TYPE_MAP = {Type.tax_type: Type for Type in [ConstantTaxRate, IncomeTaxRate]}

def tax_creator(tax_data: dict) -> TaxRatePrototype:
    """ Creates tax object instance based on type string

    :param tax_data: data to create instance with
    :type tax_data: dict
    :return: TaxRate instance
    :rtype: TaxRate
    """
    tax_type = tax_data['type'].lower()
    tax_data.pop('type')
    return TYPE_MAP[tax_type](**tax_data)
    
