""" Account class """

from decimal import Decimal

import beautiful_date as BD
import pandas as pd

from financial_planner.common import ZERO, CENTS, NEGATIVE_ONE
from financial_planner.InterestRate import InterestRate
from financial_planner.DateUnit import DateUnit
from financial_planner.Transaction import TransactionLog
from financial_planner.TaxRate import ConstantTaxRate, tax_creator, TaxRatePrototype

class Account:
    negative_balance_allowed = False
    account_type = 'Account'

    def __init__(
            self, 
            name: str = None, 
            interest_rate = 0.0, 
            balance = ZERO, 
            transactions: list = None, 
            allow_auto_withdrawl: bool = True,
            withdrawal_tax_rate: TaxRatePrototype = None) -> None:
        assert(name is not None), "All accounts must have a name!"
        self.name = name
        self.balance = Decimal(balance).quantize(CENTS)
        self.default_interest_rate = InterestRate(Decimal(interest_rate))
        if transactions is None:
            self.transactions = []
        else:
            self.transactions = transactions
        if type(allow_auto_withdrawl) == bool:
            self.allow_auto_withdrawl = allow_auto_withdrawl
        else:
            self.allow_auto_withdrawl = allow_auto_withdrawl.lower == "true"
        if withdrawal_tax_rate is None:
            self.withdrawal_tax_rate = ConstantTaxRate()
        else:
            self.withdrawal_tax_rate = withdrawal_tax_rate

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'type': 'account',
            'subtype': self.account_type,
            'negative_balance_allowed': self.negative_balance_allowed,
            'interest_rate': self.default_interest_rate.to_dict(),
            'balance': str(self.balance),
            'allow_auto_withdrawal': self.allow_auto_withdrawl,
            'transactions': [t.to_dict() for t in self.transactions],
            'withdrawal_tax_rate': self.withdrawal_tax_rate.to_dict(),
        }
    
    def calculate_interest(self, time_units: DateUnit) -> Decimal:
        return (self.balance * self.default_interest_rate.get_rate(time_units))\
                .quantize(CENTS)

    def process_transactions(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate) -> list:
        transaction_list = []
        for transaction in self.transactions:
            cost = transaction.get_cost(date, relative_date)
            if cost == ZERO:
                continue
            transaction_list.append(self.execute_transaction(
                cost,
                transaction.name,
                self.name,
                date,
            ))
            taxes = transaction.get_tax(date, cost) * NEGATIVE_ONE
            if taxes != ZERO:
                transaction_list.append(self.execute_transaction(
                    taxes,
                    transaction.name + " Tax",
                    self.name,
                    date,
                ))
            
        return transaction_list

    def execute_transaction(self, amount: Decimal, description: str, destination: str, date: BD.BeautifulDate, source: str = None) -> TransactionLog:
        self.balance += amount
        return TransactionLog(
            source,
            destination,
            description,
            amount,
            date,
        )

class Debt(Account):
    negative_balance_allowed = True
    account_type = 'Debt'

class RetirementAccount(Account):
    account_type = 'Retirement Account'

