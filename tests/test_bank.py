from decimal import Decimal

import beautiful_date as BD

from financial_planner import Bank

class FakeAccount():
    name = 'fake'
    balance = Decimal("15.00")

    def calculate_interest(self, b):
        return Decimal("1.00")

    def process_transactions(self, c):
        return {'a': 1, 'b': 2}

def test_transaction_log():
    bank = Bank([FakeAccount()])
    bank.mature('a')
    assert(len(bank.transaction_log) == 1)

    bank = Bank([FakeAccount()])
    bank.process_date('a')
    assert(len(bank.transaction_log) == 1)