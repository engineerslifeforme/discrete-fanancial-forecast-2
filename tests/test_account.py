""" Tests for account"""

from decimal import Decimal

from financial_planner import Account, AccountYaml
from financial_planner import DateUnit

def test_account():
    starting_balance = Decimal("100.00")
    account = Account('a', balance=starting_balance)
    assert(account.balance == starting_balance)

def test_account_yaml():
    account = AccountYaml({
        'name': 'a',
        'balance': '5.00'
    })
    assert(account.name == 'a')
    assert(account.balance == Decimal("5.00"))

    account = AccountYaml({
        'name': 'a',
        'transactions': {
            'monthly_income': [
                {
                    'name': 'b',
                    'amount': '2.00',
                }
            ]
        }
    })
    assert(len(account.transactions) == 1)
    assert(account.transactions[0].name == 'b')