# Purpose

Assist in financial planning

# Usage

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

## Setup

While in the repo directory:

```
pip install -r requirements.txt
pip install -e .
```

## Example

`example.yml`:

```yaml
accounts:
  - name: Checking
    balance: 5.00
```

Run simulation for 1 year:

```bash 
python financial_planner/cli.py example.yml 2023-01-01 2024-01-01
```

**Note:** This will be very boring with no income and defaulting to
0% interest.

## Tips

# Repeated Values

Use a variable to set repeats for easy modification:

```yaml
IMPORTANT_DATE: 2023-06-01
---
...
end_date: {{ IMPORTANT_DATE }}
```

# Goals

- Variable Time Scale prediction
- CLI independent from GUI

# Issues

1. Mortgages do not hit precisely $0 for some reason