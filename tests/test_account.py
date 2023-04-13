""" Tests for account"""

from decimal import Decimal

from beautiful_date import *

from financial_planner import Account
from financial_planner import MonthlyTransaction
from financial_planner.TaxRate import IncomeTaxRate

def test_account():
    starting_balance = Decimal("100.00")
    account = Account('a', balance=starting_balance)
    assert(account.balance == starting_balance)

def test_account_taxed_transactions():
    starting_balance = Decimal("0.00")
    transaction_amount = Decimal("23000.00")
    acc = Account('a', balance=starting_balance, transactions=[
        MonthlyTransaction('a', transaction_amount, tax_rate=IncomeTaxRate())
    ])
    acc.process_transactions(D.today(), D.today())
    assert(acc.balance == (transaction_amount - Decimal("120.00")))