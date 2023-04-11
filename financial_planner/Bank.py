""" Bank Class"""

from copy import deepcopy
from decimal import Decimal

import beautiful_date as BD

from financial_planner.DateUnit import DateUnit, get_date_increment
from financial_planner.Transaction import TransactionLog
from financial_planner.yaml_support import parse_transaction_dict
from financial_planner.Account import Account
from financial_planner.InterestRate import InterestRate
from financial_planner.Mortgage import MortgagePrincipal, MortgagePaymentTransaction, Mortgage
from financial_planner.common import ZERO, NEGATIVE_ONE


class Bankrupt(Exception):
    pass

class Bank:

    def __init__(self, accounts: list) -> None:
        self.accounts = accounts
        self.state_log = []
        self.transaction_log = []

    @property
    def account_map(self) -> dict:
        return {account.name: account for account in self.accounts}

    def to_dict(self) -> dict:
        return {
            'type': 'bank',
            'accounts': [a.to_dict() for a in self.accounts]
        }
    
    def mature(self, date: BD.BeautifulDate):
        if len(self.state_log) == 0:
            self.capture_state(date)
        for account in self.accounts:
            change_in_value = account.calculate_interest(DateUnit.DAYS)
            account.balance += change_in_value
            self.transaction_log.append(TransactionLog(
                None,
                account.name,
                'interest',
                change_in_value,
                date,
            ))
        self.capture_state(date)

    # def mature(self, periods: int, period_unit: DateUnit):
    #     date_increment = get_date_increment(period_unit)
    #     for _ in range(periods):
    #         self.date += date_increment
    #         for account in self.accounts:
    #             change_in_value = account.calculate_interest(period_unit)
    #             transaction = TransactionLog(
    #                 'interest',
    #                 account.name,
    #                 change_in_value,
    #                 self.date,
    #             )
    #             self.transaction_log.append(transaction)
    #             account.balance += change_in_value
    #         self.state_log.extend(self.capture_state())

    def find_next_account(self, exclude: Account = None) -> Account:
        for account in self.accounts:
            if exclude is not None:
                if exclude == account:
                    continue
            if not account.allow_auto_withdrawl:
                continue
            if account.balance > ZERO:
                return account
        raise Bankrupt("No more accounts with > $0 balance.")
    
    def process_date(self, date: BD.BeautifulDate, relative_date: BD.BeautifulDate):
        """ Process transactions associated with all accounts

        :param date: current date
        :type date: BD.BeautifulDate
        :param relative_date: start date
        :type relative_date: BD.BeautifulDate
        """
        for account in self.accounts:
            self.transaction_log.extend(account.process_transactions(date, relative_date))
            incurred_taxes = ZERO
            description = f"{account.name} Low Balance Transfer"
            while account.balance < ZERO and not account.negative_balance_allowed:                
                withdraw_account = self.find_next_account(exclude=account)
                _, transactions_taxes = self.execute_transactions(
                    abs(account.balance),
                    withdraw_account, 
                    description,
                    date,
                    deposit_account=account, 
                )
                incurred_taxes += transactions_taxes
            description += " Taxes"
            while incurred_taxes > ZERO:
                withdraw_account = self.find_next_account(exclude=account)
                # No deposit account because taxes are lost not transferred
                # No taxes on paying taxes
                paid_amount, _ = self.execute_transactions(
                    incurred_taxes,
                    withdraw_account,
                    description,
                    date,
                )
                incurred_taxes -= paid_amount
                
    def execute_transactions(self, requested_amount: Decimal, withdraw_account: Account, description: str, date: BD.BeautifulDate, deposit_account: Account = None) -> Decimal:
        if withdraw_account.balance > requested_amount:
            amount = requested_amount * NEGATIVE_ONE
        else:
            amount = withdraw_account.balance * NEGATIVE_ONE
        deposit_amount = amount * NEGATIVE_ONE
        planned_taxes = withdraw_account.withdrawal_tax_rate.get_additional_taxes(abs(amount), date)
        self.transaction_log.append(withdraw_account.execute_transaction(
            amount,
            description,
            withdraw_account.name,
            date,
        ))
        if deposit_account is not None:
            self.transaction_log.append(deposit_account.execute_transaction(
                deposit_amount,
                description,
                deposit_account.name,
                date,
            ))
        return deposit_amount, planned_taxes

    def capture_state(self, date:BD.BeautifulDate):
        self.state_log.extend([{
            'account': account.name,
            'date': date,
            'balance': account.balance,
        } for account in self.accounts])

    def create_mortgage(self, name: str = None, paid_from: Account = None, loan_amount: Decimal = None, remaining_balance: Decimal = None, terms: int = None, **kwargs) -> None:
        loan = Mortgage(name=name, balance=(Decimal("-1") * Decimal(remaining_balance)))
        self.accounts.append(loan)
        loan.transactions.append(MortgagePrincipal(
            loan_amount, 
            remaining_balance, 
            terms, 
            name=f"{name} Principal Reduction",
            **kwargs
        ))
        paid_from.transactions.append(MortgagePaymentTransaction(
            loan_amount, 
            remaining_balance, 
            terms, 
            name=f"{name} Mortgage Payment", 
            **kwargs
        ))


class BankYaml(Bank):

    def allocate_transfers(self, transfer_data: dict):
        for destination_name, transaction_data in transfer_data.items():
            for transaction, source in parse_transaction_dict(transaction_data):
                self.account_map[destination_name].transactions.append(transaction)
                opposite = deepcopy(transaction)
                opposite.amount *= Decimal("-1")
                self.account_map[source].transactions.append(opposite)

    def allocate_mortgages(self, mortgage_list: list):
        for mortgage_data in mortgage_list:
            mortgage_data['paid_from'] = self.account_map[mortgage_data['paid_from']]
            self.create_mortgage(**mortgage_data)

