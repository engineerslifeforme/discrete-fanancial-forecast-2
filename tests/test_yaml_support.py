

from financial_planner.yaml_support import parse_transaction_dict

def test_parse_transaction_dict():
    parse_transaction_dict({
        'monthly': [{
            'name': 'a',
            'amount': '541.67',
        }]
    })