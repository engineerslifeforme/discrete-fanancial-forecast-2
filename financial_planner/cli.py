""" execution """

import argparse
from pathlib import Path
import shutil

import yaml
import pandas as pd
import beautiful_date as BD
import jinja2

from financial_planner import BankYaml, AccountYaml, DATE_TYPE_STR_MAP, Simulation, parse_date

environment = jinja2.Environment()
RESULTS_DIR = Path('results')

def main():
    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)
    RESULTS_DIR.mkdir()
    yaml_path, start_date, end_date = parse_cli()
    filled_yaml_text = fill_placeholders(yaml_path.read_text())
    simulation = create_simulation(filled_yaml_text)
    simulation.run(start_date, end_date, show_progress=True)
    print(simulation.bank.state_log[-1])
    transactions = pd.DataFrame([log.to_dict() for log in simulation.bank.transaction_log])
    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions.to_csv(RESULTS_DIR / 'transactions.csv')
    transactions.set_index('date')\
                .drop('title', axis='columns')\
                .groupby([pd.Grouper(freq="M"), 'destination'])\
                .sum()\
                .reset_index(drop=False)\
                .to_csv(RESULTS_DIR / 'monthly_transactions.csv')
    state = pd.DataFrame(simulation.bank.state_log)
    state['date'] = pd.to_datetime(state['date'])
    state.set_index('date')\
         .groupby([pd.Grouper(freq="M"), 'account'])\
         .tail(1)\
         .reset_index(drop=False)\
         .to_csv(RESULTS_DIR / 'monthly_account_state.csv')

def fill_placeholders(yaml_text: str) -> str:
    if '---' not in yaml_text:
        return yaml_text
    render_content, template_content = yaml_text.split('---')
    template = environment.from_string(template_content)
    return template.render(**yaml.load(render_content, Loader=yaml.BaseLoader))

def create_simulation(yaml_text: str) -> Simulation:
    config_data = yaml.load(yaml_text, Loader=yaml.BaseLoader)
    transfer_data = {}
    account_list = []
    for entry in config_data['accounts']:
        if 'transfers' in entry:
            transfer_data[entry['name']] = entry['transfers']
            del(entry['transfers'])
        account_list.append(AccountYaml(entry))
    bank = BankYaml(account_list)
    bank.allocate_transfers(transfer_data)
    bank.allocate_mortgages(config_data.get('mortgages', []))
    return Simulation(bank)

def parse_cli():
    parser = argparse.ArgumentParser(
        prog = 'financial-planner',
        description = 'Assists in performing discrete time financial planning',
        epilog = 'Good Luck!'
    )
    parser.add_argument("financial_config_path", help="Path to financial configuration file", type=Path)
    parser.add_argument("start_date", help="Date to start simulation (YYYY-MM-DD)")
    parser.add_argument("end_date", help="Date to end simulation (YYYY-MM-DD)")
    arguments = parser.parse_args()
    provided_config_path = arguments.financial_config_path
    assert(provided_config_path.exists()), f"{provided_config_path} does not exist!  Exiting"
    return provided_config_path, parse_date(arguments.start_date), parse_date(arguments.end_date)

if __name__ == "__main__":
    main()