from pathlib import Path
from decimal import Decimal
import copy

import jinja2
import pandas as pd
import yaml

from financial_planner import (
    Account,
    RetirementAccount,
    Bank,
    TRANSACTION_MAP,
    NEGATIVE_ONE,
    TransactionPrototype,
    Mortgage,
    MortgagePaymentTransaction,
    MortgagePrincipal,
)

environment = jinja2.Environment()

def process_yaml_file(config_path: Path) -> Bank:
    config_data = yaml.load(
        fill_placeholders(config_path.read_text()), 
        Loader=yaml.BaseLoader,
    )
    return create_bank(config_data)

def create_bank(data: dict) -> Bank:
    account_map = {}
    for AccountType, accounts_data in [(Account, data.get('accounts', [])), (RetirementAccount, data.get('retirement_accounts', []))]:
        for account_data in accounts_data:
            new_account = create_account(account_data, AccountType, account_map)
            account_map[new_account.name] = new_account
    mortgage_accounts = [create_mortgage(m, account_map) for m in data.get('mortgages', [])]
    return Bank(
        list(account_map.values()) + mortgage_accounts
    )

def create_mortgage(data: dict, account_map: dict) -> Account:
    paid_from_account = account_map[data.pop('paid_from')]
    principal_data = copy.deepcopy(data)
    principal_data['name'] += 'Principal'
    mortgage = Mortgage(
        name=data['name'],
        balance=data['remaining_balance'],
        transactions=[MortgagePrincipal(**principal_data)]
    )
    payment_data = copy.deepcopy(data)
    payment_data['name'] += 'Payment'
    paid_from_account.transactions.append(MortgagePaymentTransaction(**payment_data))    
    return mortgage

def make_transactions(data: dict) -> TransactionPrototype:
    if not data.pop('income_or_expense', 'income') == 'income':
        data['amount'] = Decimal(data['amount']) * NEGATIVE_ONE        
    Transaction = TRANSACTION_MAP[data.pop('frequency_label')]
    return Transaction(**data)

def create_account(data: dict, AccountType: object, account_map: dict) -> Account:
    transactions_data_list = []
    transactions_data_list.extend(process_external_transactions(data.pop('external_transactions', {})))
    transactions_data_list.extend(process_transactions(data.pop('transactions', {})))
    transactions_data_list.extend(process_transfers(data.pop('transfers', {}), account_map))
    transactions = []
    for data_entry in transactions_data_list:
        transactions.append(
            make_transactions(data_entry)    
        )
    return AccountType(transactions=transactions, **data)

def process_transfers(data: dict, account_map: dict) -> list:
    return process_transactions(
        {'income': data},
        account_map=account_map,
    )

def process_transactions(data: dict, account_map: dict = None) -> list:
    transactions = []
    for t_type in ['income', 'expense']:
        transaction_set = data.get(t_type, {})
        for frequency_label, transaction_data in transaction_set.items():
            for entry in transaction_data:
                entry['frequency_label'] = frequency_label
                entry['income_or_expense'] = t_type
                source = entry.pop('source', None)
                transactions.append(entry)                
                if source is not None:
                    entry_copy = copy.deepcopy(entry)
                    entry_copy['amount'] = Decimal(entry_copy['amount']) * NEGATIVE_ONE
                    account_map[source].transactions.append(make_transactions(entry_copy))
    return transactions


def process_external_transactions(data_list: list) -> list:
    transactions = []
    for data in data_list:
        csv_path = data.pop('path')
        for entry in pd.read_csv(csv_path).to_dict(orient='records'):
            entry.update(data)
            transactions.append(entry)
    return transactions


def fill_placeholders(yaml_text: str) -> str:
    if '---' not in yaml_text:
        return yaml_text
    render_content, template_content = yaml_text.split('---')
    template = environment.from_string(template_content)
    return template.render(**yaml.load(render_content, Loader=yaml.BaseLoader))