## Usage

```
usage: financial-planner [-h] financial_config_path start_date end_date

Assists in performing discrete time financial planning

positional arguments:
  financial_config_path
                        Path to financial configuration file
  start_date            Date to start simulation (YYYY-MM-DD)
  end_date              Date to end simulation (YYYY-MM-DD)

options:
  -h, --help            show this help message and exit
```

Run simulation for 1 year:

```bash 
python financial_planner/cli.py example.yml 2023-01-01 2024-01-01
```