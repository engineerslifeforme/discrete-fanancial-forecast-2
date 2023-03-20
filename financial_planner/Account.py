""" Account class """

from decimal import Decimal

import beautiful_date as BD
import pandas as pd

from financial_planner.common import ZERO, CENTS
from financial_planner.InterestRate import InterestRate
from financial_planner.DateUnit import DateUnit
from financial_planner.Transaction import TransactionLog
from financial_planner.yaml_support import parse_transaction_dict, tranlate_transaction

class Account:
    negative_balance_allowed = False

    def __init__(self, name: str = None, interest_rate = 0.0, balance = ZERO, transactions: list = None, allow_auto_withdrawl: bool = True) -> None:
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

    def calculate_interest(self, time_units: DateUnit) -> Decimal:
        return (self.balance * self.default_interest_rate.get_rate(time_units))\
                .quantize(CENTS)

    def process_transactions(self, date: BD.BeautifulDate) -> list:
        transaction_list = []
        for transaction in self.transactions:
            cost = transaction.get_cost(date)
            if cost == ZERO:
                continue
            transaction_list.append(self.execute_transaction(
                cost,
                transaction.name,
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

class AccountYaml(Account):

    def __init__(self, parsed_yaml_data: dict) -> None:        
        
        transaction_data = parsed_yaml_data.get('transactions', {})
        parsed_yaml_data['transactions'] = [transaction for transaction, _ in parse_transaction_dict(transaction_data, income_vs_expense_processing=True)]

        transaction_list = []
        for external_source_info in parsed_yaml_data.get('external_transactions', []):
            external_data = pd.read_csv(external_source_info['path'], dtype=str)
            del(external_source_info['path'])
            for entry in external_data.to_dict(orient='records'):
                entry.update(external_source_info)
                transaction_list.append(tranlate_transaction(
                    entry,
                )[0])
        if len(transaction_list) > 0:
            del(parsed_yaml_data['external_transactions'])
        parsed_yaml_data['transactions'].extend(transaction_list)
        

        super().__init__(**parsed_yaml_data)