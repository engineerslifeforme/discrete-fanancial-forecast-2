""" execution """

import argparse
from pathlib import Path
import shutil

from financial_planner import (
    Simulation,
    parse_date
)
import pandas as pd
import yaml

from yaml_support import process_yaml_file

def main():
    yaml_path, start_date, end_date = parse_cli()
    results_dir = Path(f"{yaml_path.stem}_results")
    if results_dir.exists():
        shutil.rmtree(results_dir)
    results_dir.mkdir()

    simulation = Simulation(process_yaml_file(yaml_path))
    simulation_config = simulation.run(start_date, end_date, show_progress=True)
    (results_dir / 'simulation_config.yml').write_text(yaml.dump(simulation_config))
    transactions = pd.DataFrame([log.to_dict() for log in simulation.bank.transaction_log])
    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions.to_csv(results_dir / 'transactions.csv')
    transactions.set_index('date')\
                .drop('title', axis='columns')\
                .groupby([pd.Grouper(freq="M"), 'destination'])\
                .sum()\
                .reset_index(drop=False)\
                .to_csv(results_dir / 'monthly_transactions.csv')
    state = pd.DataFrame(simulation.bank.state_log)
    state['date'] = pd.to_datetime(state['date'])
    state.set_index('date')\
         .groupby([pd.Grouper(freq="M"), 'account'])\
         .tail(1)\
         .reset_index(drop=False)\
         .to_csv(results_dir / 'monthly_account_state.csv')

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