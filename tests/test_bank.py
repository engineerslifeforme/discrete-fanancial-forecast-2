from decimal import Decimal

import beautiful_date as BD

from financial_planner import Bank, BankYaml
from financial_planner.cli import create_simulation

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

def test_yaml():
    sim = create_simulation("""accounts:
- name: HSA
  interest_rate: 0.07
  balance: 50000.00
""")
    assert(sim.bank.accounts[0].balance == Decimal("50000.00"))
    sim.bank.mature(BD.D.today() + (1 * BD.days))
    assert(sim.bank.accounts[0].balance > Decimal("50000.00"))