"""YAML interface support functions"""

from decimal import Decimal

from financial_planner.Transaction import (
    MonthlyTransaction, 
    BiWeeklyTransaction, 
    TransactionPrototype,
    YearlyTransaction,
    WeeklyTransaction,
)

TRANSACTION_MAP = {
    'monthly': MonthlyTransaction,
    'biweekly': BiWeeklyTransaction,
    'yearly': YearlyTransaction,
    'weekly': WeeklyTransaction,
}

def parse_transaction_dict(transaction_data, income_vs_expense_processing: bool = False) -> list:
    converted_transaction_list = []
    if not income_vs_expense_processing:
        transaction_data = {'income': transaction_data}
    for income_or_expense, category_data in transaction_data.items():            
        for transaction_type_label, transaction_list in category_data.items():
            new_transactions = [tranlate_transaction(yaml_data, income_or_expense=income_or_expense, label=transaction_type_label) for yaml_data in transaction_list]
            converted_transaction_list.extend(new_transactions)
    return converted_transaction_list

def tranlate_transaction(transaction_data: dict, income_or_expense: str = 'income', label: str = None) -> TransactionPrototype:
    if label is None:
        label = transaction_data['frequency_label'].lower()
        del(transaction_data['frequency_label'])
    source = None
    if 'source' in transaction_data:
        source = transaction_data['source']
        del(transaction_data['source'])
    try:
        income_or_expense = transaction_data['income_or_expense'].lower()
        del(transaction_data['income_or_expense'])
    except KeyError:
        pass
    transaction = TRANSACTION_MAP[label](**transaction_data)
    if income_or_expense.lower() == 'expense':
        transaction.amount *= Decimal("-1")
    elif income_or_expense.lower() == 'income':
        pass
    else:
        print(f"ERROR: Unknown type {income_or_expense}, only income or expense allowed")
    return transaction, source
