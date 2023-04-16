from pathlib import Path

import yaml

from financial_planner import (
    Account,
    RetirementAccount,
    MonthlyTransaction,
    YearlyTransaction,
)

from yaml_support import (
    create_bank,
    create_account,
)

def load_yaml(text: str) -> dict:
    return yaml.load(text, Loader=yaml.BaseLoader)

def test_create_bank():
    bank = create_bank({})
    assert(len(bank.accounts) == 0)
    bank = create_bank(load_yaml("""accounts:
- name: a"""))
    assert(len(bank.accounts) == 1)
    bank = create_bank(load_yaml("""retirement_accounts:
- name: a"""))
    assert(len(bank.accounts) == 1)
    assert(type(bank.accounts[0]) == RetirementAccount)
    

def test_create_account():
    account = create_account(load_yaml("""name: a"""), Account, {})
    assert(len(account.transactions) == 0)
    account = create_account(load_yaml("""name: a
transactions:
    income:
        monthly:
            - name: a
              amount: 10.00"""), Account, {})
    assert(len(account.transactions) == 1)
    assert(type(account.transactions[0]) == MonthlyTransaction)

def test_transfers():
    bank = create_bank(load_yaml("""accounts:
    - name: a
    - name: b
      transfers:
        monthly:
            - name: c
              amount: 10.00
              source: a"""))
    assert(len(bank.accounts[0].transactions) == 1)
    assert(type(bank.accounts[0].transactions[0]) == MonthlyTransaction)
    assert(len(bank.accounts[1].transactions) == 1)
    assert(type(bank.accounts[1].transactions[0]) == MonthlyTransaction)

def test_mortgage():
    bank = create_bank(load_yaml("""accounts:
    - name: a
mortgages:
  - name: House Mortgage
    loan_amount: 460000
    remaining_balance: 377033.81
    terms: 180
    interest_rate: 0.0299
    paid_from: a"""))
    assert(len(bank.accounts[0].transactions) == 1)
    assert(type(bank.accounts[0].transactions[0]) == MonthlyTransaction)
    assert(len(bank.accounts[1].transactions) == 1)
    assert(type(bank.accounts[1].transactions[0]) == MonthlyTransaction)

class TestExternalTransactions:

    def setup_method(self):
        self.external_path = Path('external.csv')
        self.external_path.write_text("""name,amount,frequency_label
Summer Camp,3000,yearly
After School,385.00,monthly
Kids,100.00,monthly
Swimming,114.00,monthly
Activity,850.00,yearly""")

    def teardown_method(self):
        self.external_path.unlink()

    def test_external(self):
        account = create_account(load_yaml(f"""name: a
external_transactions:
    - path: {self.external_path}
      income_or_expense: expense"""), Account)
        assert(len(account.transactions) == 5)
        assert(type(account.transactions[0]) == YearlyTransaction)